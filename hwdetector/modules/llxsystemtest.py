#!/usr/bin/env python
import hwdetector.Detector as Detector
import utils.log as log
import json
import subprocess

log.debug("File "+__name__+" loaded")

class LlxSystemTest(Detector):
    _NEEDS=['LLIUREX_RELEASE','SYSTEMCTL_INFO','DPKG_INFO','APACHE_INFO','EPOPTES_INFO','DNSMASQ_INFO','SQUID_INFO']
    _PROVIDES=['LLXSYSTEM_TEST']

    def make_result(self,*args,**kwargs):
        ret=''
        if not ('result' in kwargs and 'msg' in kwargs):
            return
        if type(kwargs['result']) == type(list()):
            result=kwargs['result']
        else:
            result=[str(kwargs['result'])]

        for x in result:
            ret+='{}> {}: {}\n'.format(self.__class__.__name__,x,kwargs['msg'])
        return ret

    def run(self,*args,**kwargs):

        release=kwargs['LLIUREX_RELEASE']
        status=True
        msg=[]

        systemctl=kwargs['SYSTEMCTL_INFO']
        needed_services=[]
        needed_services_common=['n4d']

        if 'server' in release.lower():
            needed_services=['apache2','epoptes','dnsmasq','slapd',]
            needed_services.extend(needed_services_common)

        res_ok=[]
        res_nok=[]
        for need in needed_services:
            if need in systemctl['BYUNIT'] and systemctl['BYUNIT'][need][0]['SUB'] == 'running':
                res_ok.append(need)
            else:
                res_nok.append(need)
        msg.extend(self.make_result(result=res_ok,msg='Ok! Needed service active'))
        msg.extend(self.make_result(result=res_nok,msg='Nok! Needed service down'))


        msg=''.join(msg)
        output={'LLXSYSTEM_TEST':{'status':status,'msg':msg}}
        return output
