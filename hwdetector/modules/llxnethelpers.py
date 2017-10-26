#!/usr/bin/env python
import hwdetector.Detector as Detector
import utils.log as log
import re
import socket


log.debug("File "+__name__+" loaded")

class LlxNetHelpers(Detector):
    _PROVIDES = ['HELPER_CHECK_OPEN_PORT','HELPER_CHECK_NS']
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
            m = re.search(r'^\d+\.\d+\.\d+\.\d+$',host)
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
            socket.gethostbyname(str(args[0]))
            return True
        except:
            return False

    def run(self,*args,**kwargs):
        return {'HELPER_CHECK_OPEN_PORT':{'code':self.check_open_port,'glob':globals()},
                'HELPER_CHECK_NS':{'code':self.check_ns,'glob':globals()}
                }