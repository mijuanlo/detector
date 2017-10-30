#!/usr/bin/env python
import hwdetector.Detector as Detector
import utils.log as log
import subprocess
import re

log.debug("File "+__name__+" loaded")

class LlxServices(Detector):
    _PROVIDES = ['SYSTEMCTL_INFO','APACHE_INFO','EPOPTES_INFO','DNSMASQ_INFO','SQUID_INFO']
    _NEEDS = ['N4D_STATUS','N4D_MODULES']

    def run(self,*args,**kwargs):
        output={}

        # SYSTEMCTL
        sysctl_out=subprocess.check_output(['systemctl','--plain','--no-legend','--no-pager','list-units','--all','-t','service'])
        info={'BYUNIT':{},'BYLOAD':{},'BYACTIVE':{},'BYSUB':{}}
        for line in sysctl_out.split('\n'):
            service_info=re.search(r'(?P<UNIT>[\w\-@]+).service\s+(?P<LOAD>\S+)\s+(?P<ACTIVE>\S+)\s+(?P<SUB>\S+)\s+(?P<NAME>.*$)',line)
            if service_info:
                d=service_info.groupdict()
                #info['BYUNIT'].update({d['NAME']:d})
                for x in ['UNIT','LOAD','ACTIVE','SUB']:
                    if d[x] in info['BY'+x]:
                        info['BY'+x][d[x]].append(d)
                    else:
                        info['BY'+x][d[x]]=[d]

        output.update({'SYSTEMCTL_INFO':info})

        # APACHE
        output.update({'APACHE_INFO':None})


        # EPOPTES
        output.update({'EPOPTES_INFO':None})

        # DNSMASQ
        output.update({'DNSMASQ_INFO':None})

        # SQUID
        output.update({'SQUID_INFO':None})
        return output