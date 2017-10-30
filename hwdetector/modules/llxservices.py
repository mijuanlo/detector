#!/usr/bin/env python
import hwdetector.Detector as Detector
import utils.log as log

log.debug("File "+__name__+" loaded")

class LlxServices(Detector):
    _PROVIDES = ['SYSTEMCTL_INFO','APACHE_INFO','EPOPTES_INFO','DNSMASQ_INFO','SQUID_INFO']
    _NEEDS = ['N4D_STATUS','N4D_MODULES']

    def run(self,*args,**kwargs):
        output={}

        return output