#!/usr/bin/env python
import hwdetector.Detector as Detector
import utils.log as log
import json
import subprocess

log.debug("File "+__name__+" loaded")

class LlxNetworkTest(Detector):
    _NEEDS=['NETINFO','RESOLVER_INFO']
    _PROVIDES=['LLXNETWORK_TEST']

    def run(self,*args,**kwargs):
        msg=[]
        status=True

        netinfo=kwargs['NETINFO']
        resolution=kwargs['RESOLVER_INFO']

        # CHECK NETWORK STATUS


        # CHECK NAME RESOLUTION

        if resolution['UNRESOLVED']:
            nr=','.join(resolution['UNRESOLVED'])
            msg.append('({}) not resolvable'.format(nr))
            status=False
        if resolution['RESOLVED']:
            nr=','.join(resolution['RESOLVED'])
            msg.append('({}) Ok! it\'s resolvable'.format(nr))
            if resolution['UNREACHABLE']:
                nr=','.join(resolution['UNREACHABLE'])
                msg.append('({}) not reachable'.format(nr))
                status=False
            else:
                msg.append('({}) it\'s reachable'.format(nr))

        msg='\n'.join(msg)
        output={'LLXNETWORK_TEST':{'status':status,'msg':msg}}
        return output
