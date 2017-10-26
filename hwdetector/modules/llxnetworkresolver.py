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
        release=kwargs['LLIUREX_RELEASE']
        session=kwargs["LLIUREX_SESSION_TYPE"]
        ldap_mode=kwargs["LDAP_MODE"]

        if release.lower() == 'server' and ldap_mode.lower() == 'slave':
            print 'im slave'

        return {'RESOLVER_INFO':None}




