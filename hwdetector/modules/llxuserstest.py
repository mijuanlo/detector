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
        mounts_info=kwargs['MOUNTS_INFO']
        user_test=kwargs['USER_TEST']

        msg=['{}\n'.format(user_test)]

        msg=''.join(msg)
        return {'LLXUSERS_TEST':{'status':status,'msg':msg}}