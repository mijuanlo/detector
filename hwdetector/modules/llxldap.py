#!/usr/bin/env python
import hwdetector.Detector as Detector
import utils.log as log
import re
import base64
import hashlib

log.debug("File "+__name__+" loaded")

class LlxLdap(Detector):
    _NEEDS = ['HELPER_EXECUTE','HELPER_FILE_FIND_LINE','HELPER_UNCOMMENT','HELPER_CHECK_OPEN_PORT','LLIUREX_RELEASE','HELPER_CHECK_ROOT','NETINFO','N4D_VARS']
    _PROVIDES = ['SERVER_LDAP','LDAP_INFO','LDAP_MODE','LDAP_MASTER_IP']

    def check_files(self,*args,**kwargs):
        release=args[0]
        mode=args[1].lower()
        server=args[2]

        if mode == 'independent':
            servername = server
        else:
            servername = 'localhost'

        output={}
        content_ldap_conf=self.uncomment("/etc/ldap.conf")
        ldap_conf_ok = self.file_find_line(content_ldap_conf,
        [
            ['^base','dc=ma5,dc=lliurex,dc=net'],
            ['^uri','ldap://'+servername],
            ['^nss_base_group','ou=Groups,dc=ma5,dc=lliurex,dc=net'],
            ['^nss_map_attribute','gecos','description']
        ])
        content_etc_ldap_ldap_conf=self.uncomment("/etc/ldap/ldap.conf")
        etc_ldap_ldap_conf_ok = self.file_find_line(content_etc_ldap_ldap_conf,
        [
            ['^BASE','dc=ma5,dc=lliurex,dc=net'],
            ['^URI','ldaps://'+servername]
        ])
        if ldap_conf_ok:
            output['etc_ldap_conf']={'syntax':'OK','content':content_ldap_conf}
        else:
            output['etc_ldap_conf'] = {'syntax': 'NOK', 'content': content_ldap_conf}

        if etc_ldap_ldap_conf_ok:
            output['etc_ldap_ldap_conf']={'syntax':'OK','content':content_etc_ldap_ldap_conf}
        else:
            output['etc_ldap_ldap_conf'] = {'syntax': 'NOK', 'content': content_etc_ldap_ldap_conf}

        nsswitch_content = self.uncomment('/etc/nsswitch.conf')
        nsswitch_ok = self.file_find_line(nsswitch_content,
        [
            ['passwd:','files','ldap'],
            ['group:','files','ldap'],
            ['shadow:','files','ldap']
        ])
        if nsswitch_ok:
            output['nsswitch_conf']={'syntax':'OK','content':nsswitch_content}
        else:
            output['nsswitch_conf'] = {'syntax': 'NOK', 'content': nsswitch_content}
        return output

    def check_ports(self,*args,**kwargs):
        ports=['389','636']
        out = {}
        for p in ports:
            out[p]=self.check_open_port('server',p)
        try:
            self.file_find_line(self.execute(run='netstat -nx'),'/var/run/slapd/ldapi')
            out['LDAPI']=True
        except Exception as e:
            out['LDAPI']=False
        return out

    def parse_tree(self,*args,**kwargs):
        if type(args[0]) != type(str()):
            return None
        output = {}
        lines = args[0].split("\n")

        path = output
        atrib=''
        value=''
        for line in lines:
            if line=='':
                path=output
            else:
                if line.startswith('dn: '):
                    hierarchy=line[4:].split(',')
                    hierarchy.reverse()
                    for level in hierarchy:
                        if level not in path:
                            path[level]={}
                        path = path[level]
                elif line.startswith(' '):
                    value=value+line[1:]
                    path[atrib][-1]=value
                else:
                    parts=line.split(' ')
                    atrib=parts[0][:-1]
                    value=' '.join(parts[1:])
                    if atrib in path:
                        path[atrib].append(value)
                    else:
                        path.update({atrib:[value]})

        output=self.make_alias(output)
        return output

    def make_alias(self,*args,**kwargs):
        d=args[0]
        if len(args) == 1:
            out={}
        else:
            out = args[1]
        for k in d.keys():
            if type(d[k]) == type(dict()):
                split = k.split('=')
                if len(split) > 1:
                    aliaslevel = split[1]
                    out[aliaslevel] = self.make_alias(d[k])
            else:
                out.update({k:d[k]})
        return out

    def read_pass(self):
        self.pwd=None
        try:
            with open('/etc/ldap.secret','r') as f:
                self.pwd=f.read().strip()
        except:
            pass

    def checkpass(self,*args,**kwargs):
        p=args[0]
        if self.pwd:
            hash_digest_with_salt=base64.b64decode(base64.b64decode(p)[6:]).strip()
            salt=hash_digest_with_salt[hashlib.sha1().digest_size:]
            compare=base64.b64encode("{SSHA}" + base64.encodestring(hashlib.sha1(str(pwd) + salt).digest() + salt))
            return p == compare
        return None

    def get_ldap_config(self,*args,**kwargs):
        release=args[0].lower()
        root_mode=self.check_root()
        kw={'stderr':None}

        if root_mode:
            kw.setdefault('asroot',True)
        auth="-Y EXTERNAL"
        uri="ldapi:///"

        if release=='client' and self.pwd:
            auth="-D cn=admin,dc=ma5,dc=lliurex,dc=net -w "+self.pwd
            uri="-H ldaps://server:636"

        try:
            db=self.execute(run='ldapsearch {} -H {} -LLL'.format(auth,uri),**kw)
            tree_db=self.parse_tree(db)
        except:
            db=None
            tree_db=None
        try:
            config=self.execute(run='ldapsearch {} -H {} -b cn=config -LLL'.format(auth,uri),**kw)
            tree_config=self.parse_tree(config)
        except:
            config=None
            tree_config=None

        try:
            tree_db['net']['lliurex']['ma5']['o']
            init_done=True
        except:
            init_done=False

        if tree_config:
            good_pass=False
            if tree_config['config']['{1}mdb']['olcRootPW:'] and 'cn=admin,dc=ma5,dc=lliurex,dc=net' in tree_config['config']['{1}mdb']['olcRootDN']:
                good_pass=self.checkpass(tree_config['config']['{1}mdb']['olcRootPW:'][0])
        else:
            good_pass=None
        return {'CONFIG':tree_config,'DB':tree_db,'INITIALIZED':init_done,'SECRET_STATUS':good_pass}

    def run(self,*args,**kwargs):
        out = {'LDAP_MASTER_IP':None}
        output = {}
        release=kwargs['LLIUREX_RELEASE']
        vars=kwargs['N4D_VARS']
        mapping={'CLIENT_LDAP_URI':'SERVER_LDAP'}
        server=None
        for search_var in mapping:
            if search_var in vars and 'value' in vars[search_var]:
                output.update({mapping[search_var]:vars[search_var]['value']})
                server=vars[search_var]['value']
        self.read_pass()

        output['PORTS'] = self.check_ports()
        mode=None

        if output['PORTS']['636']:
            output['CONFIG']=self.get_ldap_config(release)
            mode='UNKNOWN'
            try:
                test=output['CONFIG']['INITIALIZED']
            except:
                mode='UNNINITIALIZED'
            try:
                test=output['CONFIG']['CONFIG']['config']['{1}mdb']['olcSyncrepl']
                test=output['CONFIG']['CONFIG']['config']['{1}mdb']['olcUpdateRef']
                mode='SLAVE'
                if output['CONFIG']['CONFIG']['config']['{1}mdb']['olcSyncrepl'][0]:
                    m=re.search(r'provider=ldapi?://(?P<LDAP_MASTER_IP>\d+\.\d+\.\d+\.\d+)',output['CONFIG']['CONFIG']['config']['{1}mdb']['olcSyncrepl'][0])
                    if m:
                        out.update(m.groupdict())
            except:# indep or master(running without permissions)
                mode='INDEPENDENT'
                netinfo=kwargs['NETINFO']
                if netinfo:
                    aliased_interfaces = [ k for k in netinfo if 'nalias' in netinfo[k] and netinfo[k]['nalias'] > 0 ]
                    for i in aliased_interfaces:
                        for n in range(netinfo[i]['nalias']):
                            if 'alias'+str(n+1)+'_ifaddr' in netinfo[i]:
                                ip_alias=netinfo[i]['alias'+str(n+1)+'_ifaddr'].split('.')[3].split('/')[0]
                                if ip_alias=='1':
                                    mode='SLAVE'
                                elif ip_alias=='254':
                                    mode='MASTER'

        output['FILES'] = self.check_files(release,mode,server)
        out.update( {'LDAP_INFO':output,'LDAP_MODE':mode})

        return out