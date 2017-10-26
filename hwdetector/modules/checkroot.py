#!/usr/bin/env python
import hwdetector.Detector as Detector
import utils.log as log
import os,sys

log.debug("File "+__name__+" loaded")

class LlxCheckroot(Detector):
    _PROVIDES=['IAMGOD']
    _NEEDS=[]

    def run(self,*args,**kwargs):
        if os.geteuid() == 0:
            return {'IAMGOD':'YES'}
        return {}
