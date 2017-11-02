#!/usr/bin/env python
import hwdetector.Detector as Detector
import utils.log as log
import json
import subprocess

log.debug("File "+__name__+" loaded")

class LlxSystemTest(Detector):
    _NEEDS=['LLIUREX_RELEASE','SYSTEMCTL_INFO','DPKG_INFO','APACHE_INFO','EPOPTES_INFO','DNSMASQ_INFO','SQUID_INFO','PROCESS_INFO']
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
        needed_services={}
        needed_services_common=[{'n4d':['n4d-server']}]

        map(needed_services.update,needed_services_common)

        if 'server' in release.lower():
            map(needed_services.update,[{'apache2':['apache2']},{'epoptes':['epoptes','socat']},{'dnsmasq':['dnsmasq']},{'slapd':['slapd']}])

        res_ok=[]
        res_nok=[]
        ps=kwargs['PROCESS_INFO']
        for need in needed_services:
            if need in systemctl['BYUNIT'] and systemctl['BYUNIT'][need][0]['SUB'] == 'running':
                res_ok.append('Service {}'.format(need))
                plist=ps.search(needed_services[need])
                for x in plist:
                    res_ok.append('{} Process matching \'{}\''.format(len(plist[x]),x))
            else:
                res_nok.append('Service {}'.format(need))
                status=False


        msg.append(self.make_result(result=res_ok,msg='Ok! Running'))
        msg.append(self.make_result(result=res_nok,msg='Nok! Down'))

        msg=''.join(msg)
        output={'LLXSYSTEM_TEST':{'status':status,'msg':msg}}
        return output
