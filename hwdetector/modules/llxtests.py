#!/usr/bin/env python
import hwdetector.Detector as Detector
import utils.log as log
import json
import subprocess

log.debug("File "+__name__+" loaded")

class LlxAlltests(Detector):
    _NEEDS=['LLXSYSTEM_TEST','LLXNETWORK_TEST']
    _PROVIDES=['ALL_TESTS']

    def run(self,*args,**kwargs):
        if kwargs['LLXNETWORK_TEST']:
            print "Network OK!"
        if kwargs['LLXSYSTEM_TEST']:
            print "System OK!"
        output={'ALL_TESTS':True}
        return output