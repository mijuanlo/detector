#!/usr/bin/env python
import hwdetector.Detector as Detector
import utils.log as log
import subprocess
import os

log.debug("File "+__name__+" loaded")

class LlxVersion(Detector):
    _PROVIDES=["LLIUREX_VERSION","LLIUREX_RELEASE","LLIUREX_SESSION_TYPE","HAS_MIRROR","ARCHITECTURE"]
    _NEEDS = []
    def run(self,*args,**kwargs):
        d={}
        output={}
        try:
            output.update({'LLIUREX_VERSION':subprocess.check_output(["lliurex-version",'-n'],stderr=open(os.devnull,'w')).strip()})

            for k,v in [ x.split('=') for x in subprocess.check_output(["lliurex-version", "-a","-e"],stderr=open(os.devnull,'w')).strip().replace('\n',' ').split(' ') ]:
                d[k]=v

            for x in ['CLIENT','DESKTOP','SERVER','INFANTIL','MUSIC','PIME']:
                if d[x] == 'yes':
                    output['LLIUREX_RELEASE']=x

            for x in ['LIVE','SEMI','FAT','THIN']:
                if d[x] == 'yes':
                    output['LLIUREX_SESSION_TYPE']=x

            if d['MIRROR'] == 'True':
                output['HAS_MIRROR'] = True
            else:
                output['HAS_MIRROR'] = False
        except:
            pass

        output['ARCHITECTURE']=subprocess.check_output(["arch"],stderr=open(os.devnull,'w')).strip()

        return output