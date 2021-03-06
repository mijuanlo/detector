#!/usr/bin/env python
import hwdetector.Detector as Detector
import utils.log as log
import re
import os
import base64,zlib


log.debug("File "+__name__+" loaded")

class LlxServices(Detector):
    _PROVIDES = ['SYSTEMCTL_INFO','APACHE_INFO','EPOPTES_INFO','DNSMASQ_INFO','SQUID_INFO','SAMBA_INFO']
    _NEEDS = ['HELPER_EXECUTE','DPKG_INFO','N4D_STATUS','N4D_MODULES','HELPER_UNCOMMENT','NETINFO','HELPER_COMPRESS_FILE','HELPER_COMPACT_FILES','HELPER_FILE_FIND_LINE']

    def run(self,*args,**kwargs):
        output={}
        dpkg_info=kwargs['DPKG_INFO']
        netinfo=kwargs['NETINFO']

        has_apache=False
        if [ x for x in dpkg_info['BYNAME'].keys() if x.lower().startswith('apache2') ]:
            has_apache=True


        # SYSTEMCTL
        sysctl_out=self.execute(run='systemctl --plain --no-legend --no-pager list-units --all -t service')
        info={'BYUNIT':{},'BYLOAD':{},'BYACTIVE':{},'BYSUB':{},'RAW':sysctl_out}
        regexp=re.compile(r'(?P<UNIT>[\w\-@]+).service\s+(?P<LOAD>\S+)\s+(?P<ACTIVE>\S+)\s+(?P<SUB>\S+)\s+(?P<NAME>.*$)')
        for line in sysctl_out.split('\n'):
            service_info=re.search(regexp,line)
            if service_info:
                d=service_info.groupdict()
                for x in ['UNIT','LOAD','ACTIVE','SUB']:
                    if d[x] in info['BY'+x]:
                        info['BY'+x][d[x]].append(d)
                    else:
                        info['BY'+x][d[x]]=[d]

        output.update({'SYSTEMCTL_INFO':info})

        # APACHE
        output.update({'APACHE_INFO':None})

        if has_apache:
            #apacheconf=''
            #files=['/etc/apache2/apache2.conf','/etc/apache2/envvars','/etc/apache2/ports.conf']
            #dirs=['/etc/apache2/conf-enabled/','/etc/apache2/mods-enabled/','/etc/apache2/sites-enabled/']
            # for dir in dirs:
            #     if os.path.exists(dir):
            #         for file in os.listdir(dir):
            #             files.append(dir+'/'+file)
            # for file in files:
            #     if os.path.exists(file):
            #         with open(file,'r') as f:
            #             apacheconf+=f.read()+"\n"
            #apacheconf=self.uncomment(apacheconf)
            apacheconf=self.compact_files(path=['/etc/apache2/apache2.conf','/etc/apache2/envvars','/etc/apache2/ports.conf','/etc/apache2/conf-enabled/','/etc/apache2/mods-enabled/','/etc/apache2/sites-enabled/'])
            try:
                syntax=self.execute(run='apachectl -t',stderr='stdout')
                if 'syntax ok' in syntax.lower():
                    syntax = 'OK'
                mod=self.execute(run='apachectl -M -S',stderr=None).split("\n")
                modules={}
                ports_used={}
                regexp=re.compile(r'^\s+(?P<module>\S+)\s+\((?P<type>static|shared)\)$')
                regexp2=re.compile(r'^\s+port\s+(?P<PORT>\d+).*$')
                for line in mod:
                    m = re.search(regexp,line)
                    if m:
                        d=m.groupdict()
                        modules.update({d['module']:d['type']})
                    m = re.search(regexp2,line)
                    if m:
                        ports_used.update(m.groupdict())

                port_in_use=False
                # TODO: CHECK PROCESS NAME FROM PORT
                if '80' in netinfo['netstat']['BYPORT']:
                    port_in_use=True
                output.update({'APACHE_INFO':{'config':apacheconf,'syntax':syntax,'modules':modules,'PORT_USED':port_in_use}})
            except Exception as e:
                output.update({'APACHE_INFO':None})
        # EPOPTES

        epoptes_info=None
        has_epoptes=False
        if [ x for x in dpkg_info['BYNAME'].keys() if x.lower().startswith('epoptes') ]:
            has_epoptes=True
        if has_epoptes:
            epoptes_info={}
            has_epoptes_server=False
            if [ x for x in dpkg_info['BYNAME'].keys() if x.lower().startswith('n4d-epoptes-server') ]:
                has_epoptes_server=True
            has_epoptes_client=False
            if [ x for x in dpkg_info['BYNAME'].keys() if x.lower().startswith('n4d-epoptes-client') ]:
                has_epoptes_client=True

            if has_epoptes_server:
                port_in_use=False
                if '2872' in netinfo['netstat']['BYPORT']:
                    port_in_use=True
                logfile = None
                file='/var/log/epoptes.log'
                if os.path.exists(file):
                    logfile = self.compress_file(file=file)
                epoptes_info={'logfile':logfile,'PORT_USED':port_in_use}

        output.update({'EPOPTES_INFO':epoptes_info})

        # DNSMASQ
        output.update({'DNSMASQ_INFO':None})
        has_dnsmasq=False
        if [ x for x in dpkg_info['BYNAME'].keys() if x.lower() == 'dnsmasq' ]:
            has_dnsmasq=True
        if has_dnsmasq:
            main_conf=self.compact_files(path=['/etc/dnsmasq.conf','/etc/dnsmasq.d/'])
            lines=self.file_find_line(main_conf,'conf-dir','=','.+',multiple_result=True)
            paths=[line[0].split('=')[1].strip() for line in lines]
            content=main_conf+'\n'+self.compact_files(path=paths)
            output.update({'DNSMASQ_INFO':{'config':content}})

        # SQUID
        output.setdefault('SQUID_INFO',None)
        has_squid=False
        if [ x for x in dpkg_info['BYNAME'].keys() if x.lower().startswith('squid') ]:
            has_squid=True
        if has_squid:
            main_conf=self.uncomment('/etc/squid/squid.conf')
            lines=self.file_find_line(main_conf,'[^\.]+\.conf"$',multiple_result=True)
            files = [ re.findall(r'"(\S+)"',f[0])[0] for f in lines]
            file_contents={}
            file_contents.setdefault('/etc/squid/squid.conf',main_conf)
            for file in files:
                file_contents.setdefault(file,self.uncomment(file))
            output.update({'SQUID_INFO':{'config':file_contents}})

        #SAMBA
        output.update({'SAMBA_INFO':None})
        has_samba=False
        if [ x for x in dpkg_info['BYNAME'].keys() if x.lower() == 'samba' ]:
            has_samba=True
        if has_samba:
            main_conf=self.uncomment('/etc/samba/smb.conf',comments=[';','#'])
            lines=self.file_find_line(main_conf,[['include','=','\S+']])
            paths=[line[0].split('=')[1].strip() for line in lines]
            content=main_conf+'\n'+self.compact_files(path=paths)
            resources_local=self.execute(run='smbclient -L localhost -N -g',stderr=None)
            resources_server=self.execute(run='smbclient -L server -N -g',stderr=None)
            output.update({'SAMBA_INFO':{'config':content,'resources_local':resources_local,'resources_server':resources_server}})

        return output