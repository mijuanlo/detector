#!/usr/bin/env python
import hwdetector.Detector as Detector
import utils.log as log

log.debug("File "+__name__+" loaded")

class LlxUsersTest(Detector):
    _NEEDS=['MOUNTS_INFO','USER_TEST']
    _PROVIDES=['LLXUSERS_TEST']

    def run(self,*args,**kwargs):
        status=True
        msg=[]

        msg=''.join(msg)
        return {'LLXUSERS_TEST':{'status':status,'msg':msg}}