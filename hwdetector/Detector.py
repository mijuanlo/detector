#!/usr/bin/env python
from functools import wraps
import utils.log as log
log.debug("File "+__name__+" loaded")

import dill as pickle
import time
import sys


class _Detector(object):
    _PROVIDES=None
    _NEEDS=None

    def __init__(self):
        log.debug("Init detector base class")

    def run(self,*args,**kwargs):
        log.warning("Running fake run method from base class")
        pass

    def toString(self):
        log.debug("Calling toString base class")
        log.debug("My name is: {}".format( __name__))
        log.debug('My needs are: {}'.format(self._NEEDS))
        log.debug('My provides are: {}'.format(self._PROVIDES))

class Detector(_Detector):
    def runner(func):
        @wraps(func)
        def wrapper(self,*args, **kwargs):
            # first argument is class instance -> "self"
            # second argument is the first param passed to instance
            ret = None
            try:
                args = args[1:]
                out = kwargs['out']
                del kwargs['out']
                ret = func(self,*args, **kwargs)
                if ret:
                    for k in ret.keys():
                        if k[0:6].lower() == 'helper':
                            ret[k]=pickle.dumps(ret[k])
                else:
                    pass
                out.send(ret)
            except Exception as e:
                log.error('Exception in plugin({}): {}'.format(self.__class__.__name__,e))
                return None
            return ret

        return wrapper

    @runner
    def _run(self,*args,**kwargs):
        stime=time.time()
        log.debug("Running wrapped plugin {}".format(self.__class__.__name__))
        if 'stderr' in kwargs:
            sys.stderr=kwargs['stderr']
        r=self.run(self,*args,**kwargs)
        rtime=time.time()-stime
        log.info("Time running wrapped plugin {} = {}".format(self.__class__.__name__,rtime))
        return r
