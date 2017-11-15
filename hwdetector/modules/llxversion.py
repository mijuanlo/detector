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
        try:
            output.update({'LLIUREX_VERSION':self.execute(run="lliurex-version -n",stderr=None)})

            for k,v in [ x.split('=') for x in self.execute(run="lliurex-version -a -e",stderr=None).replace('\n',' ').split(' ') ]:
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

            output['LOGIN_TYPE']=d['LOGIN_TYPE']
        except:
            pass

        output['ARCHITECTURE']=self.execute(run="arch",stderr=None)

        return output