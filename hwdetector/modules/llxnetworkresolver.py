#!/usr/bin/env python
import hwdetector.Detector as Detector
import utils.log as log
import subprocess
import re
from os import listdir
from os import environ
import os

log.debug("File "+__name__+" loaded")

class LlxNetworkResolver(Detector):

    _PROVIDES=["RESOLVER_INFO"]
    _NEEDS=["LLIUREX_RELEASE","LLIUREX_SESSION_TYPE",'HELPER_CHECK_OPEN_PORT','HELPER_CHECK_ROOT','HELPER_CHECK_NS','LDAP_MODE','HELPER_CHECK_PING','LDAP_MASTER_IP','N4D_VARS']

    def __init__(self,*args,**kwargs):
        self.output={'RESOLVED': [] ,'UNRESOLVED':[],'REACHABLE':[],'UNREACHABLE':[],'STATUS':True}

    def addr_checks(self,*args,**kwargs):
        ns=str(args[0])
        ip=self.check_ns(ns)
        ret=False
        if ip:
            self.output['RESOLVED'].append(ns)
            if self.check_ping(ip):
                self.output['REACHABLE'].append(ip)
                ret=True
            else:
                self.output['UNREACHABLE'].append(ip)
        else:
            self.output['UNRESOLVED'].append(ns)

        return ret

    def run(self,*args,**kwargs):
        release=kwargs['LLIUREX_RELEASE'].lower()
        session=kwargs["LLIUREX_SESSION_TYPE"].lower()
        ldap_mode=kwargs["LDAP_MODE"].lower()
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




