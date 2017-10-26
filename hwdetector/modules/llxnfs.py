#!/usr/bin/env python
import hwdetector.Detector as Detector
import utils.log as log
import subprocess
import os.path

log.debug("File "+__name__+" loaded")

class LlxNfs(Detector):
    _NEEDS = ['HELPER_UNCOMMENT']
    _PROVIDES = ['NFS_INFO']

    def check_exports(self,*args,**kwargs):
        files=[]
        if os.path.isfile('/etc/exports'):
            files.append('/etc/exports')

        if os.path.isdir('/etc/exports.d'):
            for file in os.listdir('/etc/exports.d/'):
                files.append('/etc/exports.d/'+file)
        content=[]
        for file in files:
            with open(file,'r') as f:
                content.extend(self.uncomment(f.read()))
        if content:
            content='\n'.join(content)
        else:
            content= None
        exported = subprocess.check_output(['showmount','-e','--no-headers'])
        if exported:
            exported = exported.split("\n")
        else:
            exported=None

        return {'FILES':files,'CONTENT':content,'EXPORTED':exported}


    def run(self,*args,**kwargs):
        output ={'NFS_INFO':'OK'}
        output.update(self.check_exports())
        return output