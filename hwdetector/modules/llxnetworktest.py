#!/usr/bin/env python
import hwdetector.Detector as Detector
import utils.log as log
import json
import subprocess

log.debug("File "+__name__+" loaded")

class LlxNetworkTest(Detector):
    _NEEDS=['NETINFO','RESOLVER_INFO']
    _PROVIDES=['LLXNETWORK_TEST']

    def run(self,*args,**kwargs):
        netinfo=kwargs['NETINFO']
        resolution=kwargs['RESOLVER_INFO']
        output={'LLXNETWORK_TEST':{'status':False,'msg':'Network seems down'}}
        return output
