#!/usr/bin/env python
import hwdetector.Detector as Detector
import utils.log as log
import subprocess
import re
import os
import sys

log.debug("File "+__name__+" loaded")

class LlxServices(Detector):
    _PROVIDES = ['SYSTEMCTL_INFO','APACHE_INFO','EPOPTES_INFO','DNSMASQ_INFO','SQUID_INFO']
    _NEEDS = ['N4D_STATUS','N4D_MODULES','HELPER_UNCOMMENT']

    def run(self,*args,**kwargs):
        output={}

        # SYSTEMCTL
        sysctl_out=subprocess.check_output(['systemctl','--plain','--no-legend','--no-pager','list-units','--all','-t','service'])
        info={'BYUNIT':{},'BYLOAD':{},'BYACTIVE':{},'BYSUB':{}}
        for line in sysctl_out.split('\n'):
            service_info=re.search(r'(?P<UNIT>[\w\-@]+).service\s+(?P<LOAD>\S+)\s+(?P<ACTIVE>\S+)\s+(?P<SUB>\S+)\s+(?P<NAME>.*$)',line)
            if service_info:
                d=service_info.groupdict()
                for x in ['UNIT','LOAD','ACTIVE','SUB']:
                    if d[x] in info['BY'+x]:
                        info['BY'+x][d[x]].append(d)
                    else:
                        info['BY'+x][d[x]]=[d]

        output.update({'SYSTEMCTL_INFO':info})

        # APACHE
        output.update({'APACHE_INFO':None})
        apacheconf=''
        files=['/etc/apache2/apache2.conf','/etc/apache2/envvars','/etc/apache2/ports.conf']
        dirs=['/etc/apache2/conf-enabled/','/etc/apache2/mods-enabled/','/etc/apache2/sites-enabled/']
        for dir in dirs:
            for file in os.listdir(dir):
                files.append(dir+'/'+file)
        for file in files:
                with open(file,'r') as f:
                    apacheconf+=f.read()+"\n"
        apacheconf=self.uncomment(apacheconf)
        syntax=subprocess.check_output(['apachectl','-t'],stderr=subprocess.STDOUT).strip()
        mod=subprocess.check_output(['apachectl','-M']).split("\n")
        modules={}
        for line in mod:
            m = re.search(r'\s+(?P<module>\S+)\s+\((?P<type>\S+)\)',line)
            if m:
                d=m.groupdict()
                modules.update({d['module']:d['type']})

        output.update({'APACHE_INFO':{'config':apacheconf,'syntax':syntax,'modules':modules}})
        # EPOPTES
        output.update({'EPOPTES_INFO':None})

        # DNSMASQ
        output.update({'DNSMASQ_INFO':None})

        # SQUID
        output.update({'SQUID_INFO':None})
        return output