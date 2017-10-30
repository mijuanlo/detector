#!/usr/bin/env python
import hwdetector.Detector as Detector
import utils.log as log
import json
import subprocess

log.debug("File "+__name__+" loaded")

class LlxNetworkTest(Detector):
    _NEEDS=['NETINFO','RESOLVER_INFO','HELPER_CHECK_PING','LLIUREX_RELEASE','HELPER_GET_FILE_FROM_NET']
    _PROVIDES=['LLXNETWORK_TEST']

    def make_result(self,*args,**kwargs):
        ret=''
        if not ('result' in kwargs and 'msg' in kwargs):
            return
        if type(kwargs['result']) == type(list()):
            result=kwargs['result']
        else:
            result=[str(kwargs['result'])]

        for x in result:
            ret+='{} {}\n'.format(x,kwargs['msg'])
        return ret

    def run(self,*args,**kwargs):
        msg=[]
        status=True

        netinfo=kwargs['NETINFO']
        resolution=kwargs['RESOLVER_INFO']
        release=kwargs['LLIUREX_RELEASE'].lower()

        # CHECK NETWORK STATUS

        ifaces = [x for x in netinfo.keys() if x.startswith('eth')]
        for x in ifaces:
            if netinfo[x]['state'].lower() == 'up':
                msg.append(self.make_result(result=x,msg='Ok! it\'s up'))
            else:
                msg.append(self.make_result(result=x,msg='Nok ! it\'s down (no-link)'))
                status=False

        try:
            gw=netinfo['gw']['via']
            if self.check_ping(gw):
                msg.append(self.make_result(result=gw,msg='Ok! gateway it\'s reachable'))
            else:
                status=False
                raise Exception()
        except:
            status=False
            msg.append(self.make_result(result=x,msg='Nok! gateway not reachable'))

        def check_internet(msg,proxy=False):
            try:
                if self.check_ping('8.8.8.8'):
                    msg.append(self.make_result(result='Internet',msg='Ok! conectivity available'))
                    if self.get_file_from_net('http://lliurex.net',proxy):
                        msg.append(self.make_result(result='Lliurex.net',msg='Ok! conectivity available'))
                    else:
                        msg.append(self.make_result(result='Lliurex.net',msg='Nok! conectivity not available'))
                else:
                    raise Exception()
            except Exception as e:
                msg.append(self.make_result(result='Internet',msg='Nok! connectivity not available'))
            return msg

        if release != 'client':
            check_internet(msg)
        else:
            try:
                mode= netinfo['proxy']['mode']
                if mode == 'auto':
                    pac=netinfo['proxy']['autoconfig']
                    if self.get_file_from_net(pac):
                        msg,append(self.make_result(result='Proxy autoconfig',msg='Ok! Pac file available'))
                        check_internet(msg,True)
                    else:
                        msg,append(self.make_result(result='Proxy autoconfig',msg='Nok! file not available'))
                elif mode != 'none':
                    check_internet(msg,True)
            except Exception as e:
                check_internet(msg)

        # CHECK NAME RESOLUTION

        if resolution['UNRESOLVED']:
            msg.append(self.make_result(result=resolution['UNRESOLVED'],msg='Nok ! not resolvable'))
            status=False
        if resolution['RESOLVED']:
            msg.append(self.make_result(result=resolution['RESOLVED'],msg='Ok ! it\'s resolvable'))
            if resolution['UNREACHABLE']:
                msg.append(self.make_result(result=resolution['UNREACHABLE'],msg='Nok ! not reachable'))
                status=False
            else:
                msg.append(self.make_result(result=resolution['REACHABLE'],msg='Ok! it\'s reachable'))

        msg=''.join(msg)
        output={'LLXNETWORK_TEST':{'status':status,'msg':msg}}
        return output
