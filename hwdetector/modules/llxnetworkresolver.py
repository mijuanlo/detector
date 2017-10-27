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
    _NEEDS=["LLIUREX_RELEASE","LLIUREX_SESSION_TYPE",'HELPER_CHECK_OPEN_PORT','HELPER_CHECK_NS','LDAP_MODE']

    def run(self,*args,**kwargs):
        release=kwargs['LLIUREX_RELEASE'].lower()
        session=kwargs["LLIUREX_SESSION_TYPE"].lower()
        ldap_mode=kwargs["LDAP_MODE"].lower()

        output={'RESOLVED': [] ,'UNRESOLVED':[]}

        if release == 'server': # SERVERS
            if ldap_mode == 'slave':
                for ns in ['server']:
                    if self.check_ns(ns):
                        output['RESOLVED'].append(ns)
                    else:
                        output['UNRESOLVED'].append(ns)
            elif ldap_mode == 'independent':
                for ns in ['server']:
                    if self.check_ns(ns):
                        output['RESOLVED'].append(ns)
                    else:
                        output['UNRESOLVED'].append(ns)
            elif ldap_mode == 'master':
                for ns in ['server','pmb','opac','proxy','owncloud']:
                    if self.check_ns(ns):
                        output['RESOLVED'].append(ns)
                    else:
                        output['UNRESOLVED'].append(ns)
            else:
                for ns in ['server','pmb','opac','proxy','owncloud']:
                    if self.check_ns(ns):
                        output['RESOLVED'].append(ns)
                    else:
                        output['UNRESOLVED'].append(ns)

        elif release == 'client': # CLIENTS
            for ns in ['server','pmb','opac','proxy','owncloud']:
                if self.check_ns(ns):
                    output['RESOLVED'].append(ns)
                else:
                    output['UNRESOLVED'].append(ns)

        else: # OTHERS
            for ns in []:
                if self.check_ns(ns):
                    output['RESOLVED'].append(ns)
                else:
                    output['UNRESOLVED'].append(ns)


        return {'RESOLVER_INFO': output}




