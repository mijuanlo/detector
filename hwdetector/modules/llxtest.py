#!/usr/bin/env python
import hwdetector.Detector as Detector
import utils.log as log
import json
import subprocess

log.debug("File "+__name__+" loaded")

class LlxTest(Detector):

    #_PROVIDES = ['TEST','HELPER_ECHO']
    _PROVIDES = ['TEST']
    _NEEDS = ['NETINFO']

    # def echo(*args,**kwargs):
    #     c=0
    #     o=subprocess.check_output(['ls'])
    #     for x in args:
    #         c = c + x
    #     print(c)
    #     return o

    def run(self,*args,**kwargs):
        #param=kwargs['NETINFO'].upper().replace('NULL','null')
        #netinfo=json.loads(param)
        #netinfo2=param



        #e = self.echo
        #return {'TEST':netinfo['LO'],'HELPER_ECHO': {'code':e,'glob':globals()}}

        return {'TEST': 'ok'}