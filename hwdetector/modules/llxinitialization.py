#!/usr/bin/env python
import hwdetector.Detector as Detector
import utils.log as log

log.debug("File "+__name__+" loaded")

class LlxInitialization(Detector):
    _NEEDS = ['HELPER_UNCOMMENT','LDAP_MODE']
    _PROVIDES = ['HOSTNAME','SERVER_LDAP','INTERNAL_INTERFACE','EXTERNAL_INTERFACE']



    def run(self,*args,**kwargs):
        output = {}
        n4d_vars=kwargs['N4D_VARS']
        output.update({'HOSTNAME':self.uncomment('/etc/hostname')})
        mapping={'CLIENT_LDAP_URI':'SERVER_LDAP','INTERNAL_INTERFACE':'INTERNAL_INTERFACE','EXTERNAL_INTERFACE':'EXTERNAL_INTERFACE'}
        for search_var in mapping:
            if search_var in n4d_vars:
                output.update({mapping[search_var]:n4d_vars[search_var]['value']})

        return output