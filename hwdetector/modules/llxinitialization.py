#!/usr/bin/env python
import hwdetector.Detector as Detector
import utils.log as log

log.debug("File "+__name__+" loaded")

class LlxInitialization(Detector):
    _NEEDS = ['HELPER_UNCOMMENT','LDAP_MODE','HELPER_FILE_FIND_LINE','N4D_VARS']
    _PROVIDES = ['HOSTNAME','INTERNAL_INTERFACE','EXTERNAL_INTERFACE','NFS_INITIALIZATION']



    def run(self,*args,**kwargs):
        output = {}
        ssync_from = None
        n4d_vars=kwargs['N4D_VARS']
        output.update({'HOSTNAME':self.uncomment('/etc/hostname')})
        mapping={'INTERNAL_INTERFACE':'INTERNAL_INTERFACE','EXTERNAL_INTERFACE':'EXTERNAL_INTERFACE'}
        for search_var in mapping:
            if search_var in n4d_vars and 'value' in n4d_vars[search_var]:
                output.update({mapping[search_var]:n4d_vars[search_var]['value']})
            else:
                output.update({mapping[search_var]:None})
        line=self.file_find_line(r'/lib/systemd/system/net-server\x2dsync.mount',r'What = (\d+(?:\.\d+){3}):/net/server-sync')
        if line:
            ssync_from=''.join(line)
        else:
            ssync_from=None
        output.update({'NFS_INITIALIZATION':ssync_from})

        return output