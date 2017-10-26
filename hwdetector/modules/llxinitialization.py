#!/usr/bin/env python
import hwdetector.Detector as Detector
import utils.log as log
import os.path
import os
import re
import json

log.debug("File "+__name__+" loaded")

class LlxInitialization(Detector):
    _NEEDS = ['HELPER_CHECK_OPEN_PORT','HELPER_CHECK_NS','HELPER_UNCOMMENT','IAMGOD','LDAP_MODE']
    _PROVIDES = ['HOSTNAME','N4D_VARS','N4D_STATUS','N4D_MODULES','SERVER_LDAP','INTERNAL_INTERFACE','EXTERNAL_INTERFACE']

    def check_n4d(self,*args,**kwargs):
        output ={}
        output['N4D_STATUS']={'online':str(self.check_open_port('9779'))}
        output['N4D_STATUS'].update({'resolvable':str(self.check_ns('server'))})

        try:
            if os.path.isfile('/var/log/n4d/n4d-server'):
                with open('/var/log/n4d/n4d-server','r') as f:
                    available=[]
                    failed=[]
                    lines=f.readlines()
                    ret=''
                    for line in lines:
                        ret = ret + line.strip() + "\n"
                        m = re.search(r'\s*\[(?P<pluginname>\w+)\]\s+\S+\s+\.+\s+(?P<status>\w+)?$',line.strip())
                        if m:
                            d=m.groupdict()
                            if d['status'] and d['pluginname']:
                                if d['status'].lower() == 'ok':
                                    available.append(d['pluginname'])
                                else:
                                    failed.append(d['pluginname'])

                    output['N4D_MODULES']={'available':sorted(available),'failed':sorted(failed)}
        except Exception as e:
            output['N4D_STATUS'].update({'initlog':'not available'})
            output['N4D_STATUS'].update({'initlog_error': str(e)})

        return output

    def get_variables(self,*args,**kwargs):
        vars={}
        folder='/var/lib/n4d/variables-dir/'
        if os.path.exists(folder):
            for f in os.listdir(folder):
                file=folder+'/'+f
                try:
                    with open(file,'r') as f2:
                        vars.update(json.load(f2))
                except Exception as e:
                    vars[f]='NOT_READABLE {}'.format(e)
        return vars


    def run(self,*args,**kwargs):
        output = {}
        output = self.check_n4d()
        output.update({'HOSTNAME':self.uncomment('/etc/hostname')})
        output.update({'N4D_VARS':self.get_variables()})
        mapping={'CLIENT_LDAP_URI':'SERVER_LDAP','INTERNAL_INTERFACE':'INTERNAL_INTERFACE','EXTERNAL_INTERFACE':'EXTERNAL_INTERFACE'}
        for search_var in mapping:
            if search_var in output['N4D_VARS']:
                output.update({mapping[search_var]:output['N4D_VARS'][search_var]['value']})

        return output