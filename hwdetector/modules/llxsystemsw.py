#!/usr/bin/env python
import hwdetector.Detector as Detector
import utils.log as log
import re


log.debug("File "+__name__+" loaded")

class LlxSystemSW(Detector):
    _PROVIDES = ['DPKG_INFO','HELPER_EXECUTE']
    _NEEDS = []

    def run(self,*args,**kwargs):
        output={}
        pkg_list=self.execute(run='dpkg -l').strip("\n")

        dpkg_info={'BYNAME':{},'BYSTATUS':{}}
        regexp=re.compile(r'^(?P<STATUS>\w+)\s+(?P<PACKAGE>[^:\s]+)(:(?P<PACKAGE_ARCHITECTURE>\S+))?\s+(?P<VERSION>\S+)\s+(?P<BUILD_ARCHITECTURE>\S+)\s+(?P<DESCRIPTION>.*)$')
        for line in pkg_list.split("\n"):
            pkg_info=re.search(regexp,line)
            if pkg_info:
                d=pkg_info.groupdict()
                if d['PACKAGE_ARCHITECTURE'] == None:
                    d['PACKAGE_ARCHITECTURE'] = d['BUILD_ARCHITECTURE']
                name = d['PACKAGE']
                status = d['STATUS']
                del d['PACKAGE']
                if name in dpkg_info['BYNAME']:
                    dpkg_info['BYNAME'][name].append(d)
                else:
                    dpkg_info['BYNAME'][name] =[d]
                d['NAME']=name
                del d['STATUS']
                if status in dpkg_info['BYSTATUS']:
                    dpkg_info['BYSTATUS'][status].append(d)
                else:
                    dpkg_info['BYSTATUS'][status]=[d]

        output.update({'DPKG_INFO':dpkg_info})
        return output