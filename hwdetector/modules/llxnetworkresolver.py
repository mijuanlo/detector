#!/usr/bin/env python
import hwdetector.Detector as Detector
import utils.log as log
import re

log.debug("File "+__name__+" loaded")

class LlxNetworkResolver(Detector):

    _PROVIDES=["RESOLVER_INFO"]
    _NEEDS=["LLIUREX_RELEASE","LLIUREX_SESSION_TYPE",'HELPER_CHECK_OPEN_PORT','HELPER_CHECK_ROOT','HELPER_CHECK_NS','LDAP_MODE','HELPER_CHECK_PING','LDAP_MASTER_IP','N4D_VARS']

    def __init__(self,*args,**kwargs):
        self.output={'RESOLVED': [] ,'UNRESOLVED':[],'REACHABLE':[],'UNREACHABLE':[],'STATUS':True}

    def addr_checks(self,*args,**kwargs):
        ns=str(args[0])
        ret=False
        only_ip = re.findall('\d+\.\d+\.\d+\.\d+',ns)
        go_to_ping = True

        if only_ip:
            ip = ns
        else:
            ip=self.check_ns(ns)
            if ip:
                self.output['RESOLVED'].append(ns)

            else:
                self.output['UNRESOLVED'].append(ns)
                go_to_ping=False

        if go_to_ping:
            if self.check_ping(ip):
                self.output['REACHABLE'].append(ip)
                ret=True
            else:
                self.output['UNREACHABLE'].append(ip)

        return ret

    def run(self,*args,**kwargs):
        release=kwargs['LLIUREX_RELEASE']
        if release:
            release=release.lower()
        session=kwargs["LLIUREX_SESSION_TYPE"]
        if session:
            session = session.lower()
        ldap_mode=kwargs["LDAP_MODE"]
        if ldap_mode:
            ldap_mode=ldap_mode.lower()
        ldap_master_ip=kwargs['LDAP_MASTER_IP']
        n4d_vars=kwargs['N4D_VARS']

        nslist=['server']

        if release == 'server': # SERVERS
            if ldap_mode == 'slave':
                if ldap_master_ip:
                    nslist.append(ldap_master_ip)
                else:
                    if self.check_root():
                        # if i'm root and is not set ldap_master_ip, there is an error
                        # If i'm not root, ldap_master_ip is impossible to get from ldap
                        self.output['STATUS']=False

                    if n4d_vars['MASTER_SERVER_IP'] and n4d_vars['MASTER_SERVER_IP']['value']:
                        nslist.append(n4d_vars['MASTER_SERVER_IP']['value'])
                    else:
                        self.output['STATUS']=False

            elif ldap_mode == 'independent':
                pass
            elif ldap_mode == 'master':
                pass
            else:
                pass
        elif release == 'client': # CLIENTS
            nslist.extend(['pmb','opac','proxy','owncloud'])
        else: # OTHERS
            pass

        for ns in nslist:
            r = self.addr_checks(ns)
            if not r:
                self.output['STATUS']=False

        return {'RESOLVER_INFO': self.output}




