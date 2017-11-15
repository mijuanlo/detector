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
    _NEEDS=['HELPER_EXECUTE','HELPER_COMPRESS_FILE','HELPER_LIST_FILES']
    _PROVIDES=['LSHW_INFO','DMESG_INFO','VARLOG_INFO','LSUSB_INFO','DMESG_JOURNAL_INFO','SYSCTL_INFO']

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
        regexp=re.compile(r'^[^\.]+(\.log|(\.\d+)+)?$')
        #filter=lambda x: [ f for f in x if re.match(regexp,f)]

        try:
            #prefix='/var/log'
            #file_names=[]
            #for root,dirnames,filenames in os.walk(prefix):
            #    for filename in filter(filenames):
            #        file_names.append(os.path.join(root,filename))
            file_names=self.list_files(path='/var/log',regexp=regexp)
            for file in file_names:
                varlog[os.path.basename(file)]=self.compress_file(file=file)
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

    def get_sysctl(self,*args,**kwargs):
        def make_hierarchy(d={},l=[],value=None):
            if len(l) > 1:
                d.setdefault(l[0],{})
                return make_hierarchy(d[l[0]],l[1:],value)
            else:
                return d.setdefault(l[0],value)
        d={}
        for key_value in self.execute(run='sysctl -a',stderr=None).split('\n'):
            key,value=key_value.split(' = ')
            make_hierarchy(d,key.split('.'),value)
        return d

    def run(self,*args,**kwargs):
        output={'LSHW_INFO':{},'DMESG_INFO':{},'SYSLOG_INFO':{},'LSUSB_INFO':{}}

        output['LSHW_INFO']=self.get_lshw()
        output['DMESG_INFO']=self.get_dmesg2()
        output['DMESG_JOURNAL_INFO']=self.get_dmesg()
        output['VARLOG_INFO']=self.get_varlog()
        output['LSUSB_INFO']=self.get_lsusb()
        output['SYSCTL_INFO']=self.get_sysctl()

        return output