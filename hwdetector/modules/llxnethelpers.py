#!/usr/bin/env python
import hwdetector.Detector as Detector
import utils.log as log
import re
import socket
import subprocess
import os


log.debug("File "+__name__+" loaded")

class LlxNetHelpers(Detector):
    _PROVIDES = ['HELPER_CHECK_OPEN_PORT','HELPER_CHECK_NS','HELPER_CHECK_PING']
    _NEEDS = []

    def check_open_port(self,*args,**kwargs):
        if len(args) > 2 or len(args) == 0:
            return
        if len(args) == 1:
            port = str(args[0])
            host='127.0.0.1'
            m=re.search(r'^\d+$',port)
            if m:
                port=int(args[0])
            else:
                return False
        else:
            host=str(args[0])
            #split protocol if there is something
            host=re.findall(r'(?:[^/]+/+)?(.*)$',host)[0]
            m = re.search(r'^(\d+(?:\.\d+){3})$',host)
            if not m:
                if not self.check_ns(host):
                    return False
            port=str(args[1])
            m = re.search(r'^\d+$', port)
            if m:
                port = int(port)
            else:
                return False

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        res = sock.connect_ex((host,port))
        sock.close()
        if res == 0:
            return True
        else:
            return False

    def check_ns(self,*args,**kwargs):
        if len(args) > 1:
            return None
        try:
            ip=socket.gethostbyname(str(args[0]))
            return ip
        except:
            return False

    def check_ping(selfs,*args,**kwargs):
        if len(args) != 1:
            return None
        ret=False
        try:
            r=subprocess.check_call(['ping','-W1','-c1',str(args[0])],stderr=open(os.devnull,'w'),stdout=open(os.devnull,'w'))
            if r==0:
                ret=True
        except:
            pass
        return ret

    def run(self,*args,**kwargs):
        return {'HELPER_CHECK_OPEN_PORT':{'code':self.check_open_port,'glob':globals()},
                'HELPER_CHECK_NS':{'code':self.check_ns,'glob':globals()},
                'HELPER_CHECK_PING':{'code':self.check_ping,'glob':globals()}
                }