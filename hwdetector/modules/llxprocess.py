#!/usr/bin/env python
import hwdetector.Detector as Detector
import utils.log as log
import re

log.debug("File "+__name__+" loaded")

class Object(object):
    def search(self,*args,**kwargs):
        f=lambda n: [ x for x in self.output if n in x['FULL_CMD']]
        l=[]
        for x in args:
            if type(x) == type(list()):
                l.extend(x)
            else:
                l.extend([x])

        ret={}
        for i in l:
            list_proc_matched=f(i)
            if list_proc_matched:
                ret[i]=list_proc_matched
            else:
                ret[i]=None
        return ret

class LlxProcess(Detector):

    _PROVIDES = ['PROCESS_INFO']
    _NEEDS = []

    def run(self,*args,**kwargs):
        output=[]

        psout=self.execute(run='ps --no-headers -Awwo pid,euid,egid,args')
        regexp=re.compile(r'(?P<PID>\d+)\s+(?P<EUID>\d+)\s+(?P<EGID>\d+)\s+(?P<FULL_CMD>.*)$')
        for line in psout.split("\n"):
            m=re.search(regexp,line)
            if m:
                output.append(m.groupdict())

        o=Object()
        o.output=output

        return {'PROCESS_INFO': o}