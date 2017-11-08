#!/usr/bin/env python
import hwdetector.Detector as Detector
import utils.log as log

log.debug("File "+__name__+" loaded")

class LlxInitialization(Detector):
    _NEEDS = ['HELPER_UNCOMMENT','LDAP_MODE','HELPER_FILE_FIND_LINE','N4D_VARS']
    _PROVIDES = ['HOSTNAME','SERVER_LDAP','INTERNAL_INTERFACE','EXTERNAL_INTERFACE','NFS_INITIALIZATION']



    def run(self,*args,**kwargs):
        output = {}
        ssync_from = None
        n4d_vars=kwargs['N4D_VARS']
        output.update({'HOSTNAME':self.uncomment('/etc/hostname')})
        mapping={'CLIENT_LDAP_URI':'SERVER_LDAP','INTERNAL_INTERFACE':'INTERNAL_INTERFACE','EXTERNAL_INTERFACE':'EXTERNAL_INTERFACE'}
        for search_var in mapping:
            if search_var in n4d_vars:
                output.update({mapping[search_var]:n4d_vars[search_var]['value']})
        line=r'What = (\d+(?:\.\d+){3}):/net/server-sync'
        line=''.join(self.file_find_line(r'/lib/systemd/system/net-server\x2dsync.mount',line))
        if line:
            ssync_from=line
        output.update({'NFS_INITIALIZATION':ssync_from})

        return output