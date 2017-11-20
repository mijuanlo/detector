#!/usr/bin/env python
import hwdetector.Detector as Detector
import utils.log as log

log.debug("File "+__name__+" loaded")

class LlxVersion(Detector):
    _PROVIDES=["LLIUREX_VERSION","LLIUREX_RELEASE","LLIUREX_SESSION_TYPE","HAS_MIRROR","ARCHITECTURE",'LOGIN_TYPE']
    _NEEDS = ['HELPER_EXECUTE']
    def run(self,*args,**kwargs):
        d={}
        output={}
        output.setdefault('LLIUREX_VERSION',None)
        output.update({'LLIUREX_VERSION':self.execute(run="lliurex-version -n",stderr=None)})

        try:
            for k,v in [ x.split('=') for x in self.execute(run="lliurex-version -a -e",stderr=None).replace('\n',' ').split(' ') ]:
                d[k]=v
        except:
            pass

        output.setdefault('LLIUREX_RELEASE',None)
        for x in ['CLIENT','DESKTOP','SERVER','INFANTIL','MUSIC','PIME']:
            if x in d and d[x].lower() == 'yes':
                output['LLIUREX_RELEASE']=x

        output.setdefault('LLIUREX_SESSION_TYPE',None)
        for x in ['LIVE','SEMI','FAT','THIN']:
            if x in d and d[x].lower() == 'yes':
                output['LLIUREX_SESSION_TYPE']=x

        if 'MIRROR' in d and d['MIRROR'].lower() == 'true':
            output['HAS_MIRROR'] = True
        else:
            output['HAS_MIRROR'] = False

        output.setdefault('LOGIN_TYPE',None)
        if 'LOGIN_TYPE' in d:
            output['LOGIN_TYPE']=d['LOGIN_TYPE']

        output['ARCHITECTURE']=self.execute(run="arch",stderr=None)

        return output