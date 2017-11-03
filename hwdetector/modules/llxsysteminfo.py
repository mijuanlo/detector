#!/usr/bin/env python
import hwdetector.Detector as Detector
import utils.log as log
import json
import subprocess
import os
#import fnmatch
import re

log.debug("File "+__name__+" loaded")

class LlxSystemInfo(Detector):
    _NEEDS=[]
    _PROVIDES=['LSHW_INFO','DMESG_INFO','VARLOG_INFO','LSUSB_INFO','DMESG_JOURNAL_INFO']

    def get_lshw(self,*args,**kwargs):
        try:
            lsusb=json.loads(subprocess.check_output(['lshw','-json'],stderr=open(os.devnull,'w')))
            return lsusb
        except Exception as e:
            return None

    def get_dmesg(self,*args,**kwargs):
        try:
            dmesg=json.loads(subprocess.check_output(['journalctl','-o','json','--dmesg','--reverse','--since','today']))
            return dmesg
        except Exception as e:
            return None

    def get_dmesg2(self,*args,**kwargs):
        try:
            dmesg=subprocess.check_output(['dmesg'])
            return dmesg
        except Exception as e:
            return None

    def get_varlog(self,*args,**kwargs):
        varlog={}
        regexp=re.compile(r'\w+(\.log)?$')
        filter=lambda x: [ f for f in x if re.match(regexp,f)]

        try:
            prefix='/var/log'
            file_names=[]
            for root,dirnames,filenames in os.walk(prefix):
                for filename in filter(filenames):
                    file_names.append(os.path.join(root,filename))
            for file in file_names:
                try:
                    with open(file,'r') as f:
                        varlog[os.path.basename(file)]=f.read().strip()
                except Exception as e:
                    pass
        except Exception as e:
            return None
        return varlog

    def get_lsusb(self,*args,**kwargs):
        lsusb={}
        try:
            lsusb=subprocess.check_output(['lsusb'],stderr=open(os.devnull,'w'))
            return lsusb
        except Exception as e:
            return None

    def run(self,*args,**kwargs):
        output={'LSHW_INFO':{},'DMESG_INFO':{},'SYSLOG_INFO':{},'LSUSB_INFO':{}}

        output['LSHW_INFO']=self.get_lshw()
        output['DMESG_INFO']=self.get_dmesg2()
        output['DMESG_JOURNAL_INFO']=self.get_dmesg()
        output['VARLOG_INFO']=self.get_varlog()
        output['LSUSB_INFO']=self.get_lsusb()

        return output