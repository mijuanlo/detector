#!/usr/bin/env python
import hwdetector.Detector as Detector
import utils.log as log
import json
import subprocess

log.debug("File "+__name__+" loaded")

class LlxNetworkTest(Detector):
    _NEEDS=['NETINFO']
    _PROVIDES=['LLXNETWORK_TEST']

    def run(self,*args,**kwargs):
        output={'LLXNETWORK_TEST':True}
        return output
