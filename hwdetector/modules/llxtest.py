#!/usr/bin/env python
import hwdetector.Detector as Detector
import utils.log as log
import json
import subprocess

log.debug("File "+__name__+" loaded")

class CTest(object):
    def __init__(self,*args,**kwargs):
        try:
            val=int(args[0])
        except:
            val = 10
        self.attrib=range(val)

    def toString(self,*args,**kwargs):
        status=True
        if 'range' in kwargs:
            range_val=int(kwargs['range'])
            self.attrib=range(range_val)
            status=False

        for x in self.attrib:
            print x

        return status

def toString2(*args,**kwargs):
    try:
        for x in self.attrib:
            print x
        return True
    except:
        for x in range(1,3):
            print x
        return True
    return False

class DetectorObject(object):
    pass

class LlxTest(Detector):

    #_PROVIDES = ['TEST','HELPER_ECHO']
    _PROVIDES = ['TEST']
    _NEEDS = []

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
        #t=CTest(5)
        #return {'TEST':  t}
        t=DetectorObject()
        setattr(t,'attrib',range(10))
        #t.attrib=range(10)
        t.to_string = toString2
        return {'TEST':t}