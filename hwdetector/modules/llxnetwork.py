#!/usr/bin/env python
import hwdetector.Detector as Detector
import utils.log as log
import re
from os import listdir
from os import environ

log.debug("File "+__name__+" loaded")

class LlxNetwork(Detector):

    _PROVIDES=["NETINFO"]
    _NEEDS=['HELPER_UNCOMMENT',"HELPER_GET_FILE_FROM_NET","HELPER_EXECUTE",'HELPER_COMPACT_FILES']

    def get_routes(self,*args,**kwargs):
        routes = self.execute(run="ip r",stderr=None)
        if not routes:
            return None
        else:
            routes=routes.split("\n")
            rt = {}
            rt['names'] = {}
            rt['names']['bynet'] = {}
            rt['names']['byiface'] = {}
            for line in routes:
                if 'default' in line:
                    m = re.search(r'default via (?P<via>\S+) dev (?P<dev>\w+)', line)
                    d = m.groupdict()
                    if not d['dev'] in rt:
                        rt[d['dev']] = []
                    rt[d['dev']].append({'src': '0.0.0.0', 'net': d['via']})
                    rt['names']['default'] = {'via': d['via'], 'dev': d['dev']}
                    rt['names']['gw'] = d['via']
                else:
                    m = re.search(
                        r'(?P<net>\S+) dev (?P<dev>\w+)\s+(?:proto kernel)?\s+scope link\s+(?:metric \d+)?\s+(?:src (?P<src>\S+))?',
                        line)
                    d = m.groupdict()
                    if not 'src' in d or d['src'] == None:
                        d['src'] = 'unknown'
                    if not d['dev'] in rt:
                        rt[d['dev']] = []
                    rt[d['dev']].append({'src': d['src'], 'net': d['net']})
                    rt['names']['byiface'][d['src']] = d['net']
                    rt['names']['bynet'][d['net']] = d['src']
            return rt

    def get_resolver(self,*args,**kwargs):
        resolv_lines=self.uncomment('/etc/resolv.conf')
        output={}
        for line in resolv_lines.split("\n"):
            m=re.search(r'(?:nameserver\s+(?P<nameserver>\S+)|search\s+(?P<search>\w+)|domain\s+(?P<domain>\w+))',line)
            if m:
                d=m.groupdict()
                for key in ['nameserver','search','domain']:
                    if key in d and d[key] != None:
                        output[key]=d[key]
        return output


    def get_ifaces(self,*args,**kwargs):
        devs = listdir("/sys/class/net/")
        output = {}
        regif = []
        regif.append(r"\d+: (?P<iface>\w+):")
        regif.append(r"mtu (?P<mtu>\d+)")
        regif.append(r"state (?P<state>UNKNOWN|UP|DOWN)")
        regif.append(r"link/(?:loopback|ether) (?P<ether>\S+) brd (?P<bether>\S+)")
        regif.append(
            r'inet (?P<ifaddr>\S+)(?: brd (?P<bcast>\S+))? scope (?:global|host) (?:dynamic )?(?P<type>\w+(?::\w+)?)(\s+valid_lft \S+ preferred_lft \S+\s+)')

        for dev in devs:
            aliasnum = 1
            info = self.execute(run="ip addr show "+dev,stderr=None).replace("\n", "")
            for i in range(0, len(regif)):
                m = [x for x in re.finditer(regif[i], info)]
                for x in m:
                    d = x.groupdict()
                    if 'iface' in d:
                        iface = d['iface']
                        output[iface] = {}
                    else:
                        if 'type' in d:
                            if ':' in d['type']:
                                for x in d:
                                    output[iface].update({'alias' + str(aliasnum) + '_' + x: d[x]})
                                aliasnum = aliasnum + 1
                            else:
                                #d.update({'nalias':0})
                                output[iface].update(d)
                        else:
                            output[iface].update(d)
            if aliasnum > 1:
                output[iface].update({'nalias': aliasnum - 1})
                aliasnum = 1
        return output

    def get_proxy(self,*args,**kwargs):
        output={}
        done=False
        for x in environ:
            if 'proxy' in x.lower():
                output[x]=environ[x]

        try:
            o = self.execute(run="dconf dump /system/proxy/",stderr=None)
            save_next=False
            prev= None
            skip_line=False
            for line in o.split("\n"):
                line=line.strip()
                if line == "":
                    continue
                if skip_line:
                    skip_line=False
                keys=['[/]', '[http]', '[https]']
                store_keys=['autoconfig','http','https']
                for keynum in range(len(keys)):
                    if keys[keynum] in line:
                        save_next = True
                        prev = store_keys[keynum]
                        skip_line=True
                        break
                if skip_line:
                    continue
                if save_next:
                    m = re.search(r"(?:autoconfig-url=\'(?P<autoconfig>\S+)\'|mode=\'(?P<mode>\w+)\'|host=\'(?P<host>\S+)\'|port=(?P<port>\d+))",line)
                    if m:
                        d=m.groupdict()
                        if not prev in output:
                            output[prev] = {}
                        for x in d:
                            if d[x] != None:
                                output[prev][x]=d[x]
                    else:
                        save_next=False
                        prev=None
        except Exception as e:
            raise(e)

        if 'autoconfig' in output:
            pacfile=self.get_file_from_net(output['autoconfig']['autoconfig'])
            if pacfile:
                output['autoconfig']['pacfile'] = pacfile
            else:
                output['autoconfig']['pacfile'] = ''

        return output

    def get_listens(self,*args,**kwargs):
        netstat_listen=self.execute(run='netstat -4tuln',stderr=None).split("\n")
        # TODO:CHECK PROCESS USING PORT AND STORE IT
        regexp=re.compile(r'(?P<PROTO>\w+)\s+\d+\s+\d+\s+(?P<LISTEN_ON>[^:\s]+):(?P<PORT>\d+)\s+.*$')
        netstat_info={'BYPROTO':{},'BYPORT':{}}
        for line in netstat_listen:
            listen_info = re.search(regexp,line)
            if listen_info:
                d=listen_info.groupdict()
                proto=d['PROTO']
                port=d['PORT']
                if proto not in netstat_info['BYPROTO']:
                    netstat_info['BYPROTO'][proto]={}
                if port in netstat_info['BYPROTO'][proto]:
                    netstat_info['BYPROTO'][proto][port].append(d['LISTEN_ON'])
                else:
                    netstat_info['BYPROTO'][proto][port]=[d['LISTEN_ON']]

                if port not in netstat_info['BYPORT']:
                    netstat_info['BYPORT'][port]={}
                if proto in netstat_info['BYPORT'][port]:
                    netstat_info['BYPORT'][port][proto].append(d['LISTEN_ON'])
                else:
                    netstat_info['BYPORT'][port][proto]=[d['LISTEN_ON']]
        return netstat_info

    def run(self,*args,**kwargs):
        rt=self.get_routes()
        output=self.get_ifaces()

        for dev in output:
            if 'ifaddr' in output[dev] and output[dev]['ifaddr']:
                ip=output[dev]['ifaddr'].split('/')[0]
                try:
                    output[dev]['net']=rt['names']['byiface'][ip]
                except:
                    pass
        output['routes']=rt
        output['gw']=rt['names']['default']
        resolv=self.get_resolver()
        output['resolver']=resolv

        proxy=self.get_proxy()
        output['proxy']=proxy

        output['netstat']=self.get_listens()
        output['network_interfaces']=self.compact_files(path=['/etc/network/interfaces','/etc/network/interfaces.d/'])
        output['iptables_rules']=self.execute(run='iptables -L',stderr=None,asroot=True)
        forward=self.execute(run='sysctl -n net.ipv4.ip_forward',stderr=None)
        if forward == '1':
            output['forwading']=True
        else:
            output['forwading']=False
        #s=json.dumps(output)

        return {'NETINFO':output}
