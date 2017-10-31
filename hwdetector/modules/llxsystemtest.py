#!/usr/bin/env python
import hwdetector.Detector as Detector
import utils.log as log
import json
import subprocess

log.debug("File "+__name__+" loaded")

class LlxSystemTest(Detector):
    #_NEEDS=['LDAP_INFO','LDAP_MODE','LDAP_MASTER_IP','N4D_STATUS','USER_TEST']
    _NEEDS=['SYSTEMCTL_INFO','DPKG_INFO','APACHE_INFO','EPOPTES_INFO','DNSMASQ_INFO','SQUID_INFO']
    _PROVIDES=['LLXSYSTEM_TEST']

    def run(self,*args,**kwargs):
        output={'LLXSYSTEM_TEST':{'status':True,'msg':'OK!'}}
        return output
