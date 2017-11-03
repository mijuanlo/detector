#!/usr/bin/env python
import hwdetector.Detector as Detector
import utils.log as log

log.debug("File "+__name__+" loaded")

class LlxUsersTest(Detector):
    _NEEDS=['MOUNTS_INFO','USER_TEST']
    _PROVIDES=['LLXUSERS_TEST']

    def run(self,*args,**kwargs):
        output={}

        return {'LLXUSERS_TEST':output}