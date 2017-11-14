#!/usr/bin/env python
import hwdetector.Detector as Detector
import utils.log as log
import json
import os
import re
import base64
import zlib

log.debug("File "+__name__+" loaded")

class LlxSystemInfo(Detector):
    _NEEDS=['HELPER_EXECUTE','HELPER_COMPRESS_FILE']
    _PROVIDES=['LSHW_INFO','DMESG_INFO','VARLOG_INFO','LSUSB_INFO','DMESG_JOURNAL_INFO']

    def get_lshw(self,*args,**kwargs):
        try:
            lsusb=json.loads(self.execute(run='lshw -json',stderr=None))
            return lsusb
        except Exception as e:
            return None

    def get_dmesg(self,*args,**kwargs):
        try:
            dmesg=json.loads(self.execute(run='journalctl -o json --dmesg --reverse --since today',stderr=None))
            return dmesg
        except Exception as e:
            return None

    def get_dmesg2(self,*args,**kwargs):
        try:
            dmesg=self.execute(run='dmesg',stderr=None)
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
                #try:
                #    with open(file,'r') as f:
                #        varlog[os.path.basename(file)]=('__gz__',base64.b64encode(zlib.compress(f.read().strip())))
                #except Exception as e:
                #    pass
                varlog[os.path.basename(file)]=self.compress_file(file)
        except Exception as e:
            return None
        return varlog

    def get_lsusb(self,*args,**kwargs):
        lsusb={}
        try:
            lsusb=self.execute(run='lsusb',stderr=None)
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