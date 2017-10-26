#!/usr/bin/env python
import hwdetector.Detector as Detector
import utils.log as log
import re
import os
import subprocess
import json

log.debug("File "+__name__+" loaded")

class LlxMounts(Detector):

    _PROVIDES = ['MOUNTS_INFO']
    _NEEDS = []

    def parse_findmnt(self,*args,**kwargs):
        ltree=args[0]
        output = []
        if type(ltree) == type(dict()):
            d={}
            source=ltree['source']
            m=re.search(r'(?P<source>/[\/\w:]+)(\[(?P<bind>\S+)\])?',source)
            if m:
                tmp=m.groupdict()
                if tmp['bind']:
                    d['device'] = tmp['bind']
                    d['binding'] = tmp['source']
                else:
                    d['device'] = tmp['source']
            d['mount_path'] = ltree['target']
            d['type'] = ltree['fstype']
            d['options'] = ltree['options'].split(',')
            output.append(d)
            if 'children' in ltree:
                for ch in ltree['children']:
                    output.extend((self.parse_findmnt(ch)))
        if type(ltree) == type(list()):
            for x in ltree:
                output.extend(self.parse_findmnt(x))

        return output

    def get_mounts(self,*args,**kwargs):
        findmnt = json.loads(subprocess.check_output(['findmnt','-J'],stderr=open(os.devnull,'w')))
        mounts = self.parse_findmnt(findmnt['filesystems'])
        output = {'PSEUDO':[],'DISK':[],'NETWORK':[],'BIND':[],'OTHER':[]}
        #mounts =[]
        #with open('/proc/mounts', 'r') as f:
        #    reg = re.compile(r'^(?P<device>\S+)\s(?P<mount_path>\S+)\s(?P<type>\S+)\s(?P<options>\S+)\s(?P<dump>\S+)\s(?P<pass>\S+)$')
        #    for line in f.readlines():
        #        m = re.search(reg,line)
        #        if m:
        #            d=m.groupdict()
        #            d['options']=d['options'].split(',')
        #            mounts.append(d)

        mapping = {'PSEUDO': {'type':['sysfs','proc','devtmpfs','devpts','tmpfs','securityfs','cgroup','pstore','autofs','mqueue','debugfs','hugetlbfs','rpc_pipefs','fusectl','binfmt_misc','nfsd','gvfsd-fuse']},
                   'NETWORK':{'type':['nfs']},
                   'DISK':{'device':['/dev/']},
                   'BIND':{'binding':['/']} # 'B'ind is tested first, before 'D'isc
                   }
        for mount in mounts:
            done = False
            for type_mapping in mapping:
                for by in mapping[type_mapping]:
                    if by in mount:
                        for string in mapping[type_mapping][by]:
                            if string in mount[by]:
                                output[type_mapping].append(mount)
                                done=True
                                break
                        if done:
                            break
                if done:
                    break
            if not done:
                output['OTHER'].append(mount)

        return output

    def run(self,*args,**kwargs):
        output = {'MOUNTS_INFO':None}
        output['MOUNTS_INFO']=self.get_mounts()

        return output