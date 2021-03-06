#!/usr/bin/env python
import hwdetector.Detector as Detector
import utils.log as log
import sys

log.debug("File "+__name__+" loaded")

class LlxAlltests(Detector):
    _NEEDS=['LLXSYSTEM_TEST','LLXNETWORK_TEST','LLXUSERS_TEST']
    _PROVIDES=['ALL_TESTS']

    def run(self,*args,**kwargs):
        ret=True
        for test in self._NEEDS:
            if kwargs[test]['status']:
                pass
                #sys.stderr.write("{}>>>Testing {} was OK!\n".format(kwargs[test]['msg'],test))
            else:
                pass
                #sys.stderr.write("{}>>>Testing {} was Failed!\n".format(kwargs[test]['msg'],test))
                ret=False
        output={'ALL_TESTS':ret}
        return output