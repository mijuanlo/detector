#!/usr/bin/env python
import hwdetector.Detector as Detector
import utils.log as log
import re
import os

log.debug("File "+__name__+" loaded")

class LlxMounts(Detector):

    _PROVIDES = ['MOUNTS_INFO','FSTAB','DISK_IDS','SERVER_SYNC_INFO']
    _NEEDS = ['HELPER_COMPRESS_FILE','HELPER_UNCOMMENT','HELPER_EXECUTE']

    # def parse_findmnt(self,*args,**kwargs):
    #     ltree=args[0]
    #     output = []
    #     if type(ltree) == type(dict()):
    #         d={}
    #         source=ltree['source']
    #         m=re.search(r'(?P<source>/[\/\w:]+)(\[(?P<bind>\S+)\])?',source)
    #         if m:
    #             tmp=m.groupdict()
    #             if tmp['bind']:
    #                 d['mount_source'] = tmp['bind']
    #                 d['binding'] = tmp['source']
    #             else:
    #                 d['mount_source'] = tmp['source']
    #         d['mount_path'] = ltree['target']
    #         d['fstype'] = ltree['fstype']
    #         d['options'] = ltree['options'].split(',')
    #         output.append(d)
    #         if 'children' in ltree:
    #             for ch in ltree['children']:
    #                 output.extend((self.parse_findmnt(ch)))
    #     if type(ltree) == type(list()):
    #         for x in ltree:
    #             output.extend(self.parse_findmnt(x))
    #
    #     return output
    #
    # def complete_binding_mapping(self,*args,**kwargs):
    #     list = args[0]
    #     list_bindings = [ (x,list.index(x)) for x in list if 'binding' in x ]
    #     list_sources = []
    #     for b,idx in list_bindings:
    #         list_sources = [ (x,list.index(x)) for x in list if 'device' in x and x['device'] == b['binding']]
    #         k=0
    #         for s,idx2 in list_sources:
    #             k+=1
    #             list[idx]['binding_source_link'+str(k)]=s
    #     return list

    def parse_self_mountinfo(self,*args,**kwargs):
        def unescape(string):
            return re.sub(r'\\([0-7]{3})',(lambda m: chr(int(m.group(1),8))),string)

        mounts = {}

        with open('/proc/self/mountinfo','r') as f:
            for line in f:
                values = line.rstrip().split(' ')
                mid, pid, devid, root, mp, mopt = tuple(values[0:6])
                tail = values [7:]
                extra = []
                for item in tail:
                    if item != '-':
                        extra.append(item)
                    else:
                        break
                fstype, src, fsopt = tail[len(extra)+1:]
                mount = {'mid':int(mid),'pid':int(pid),'devid':devid,'root':unescape(root),'mount_point':unescape(mp),'mount_options':mopt,'optional_fields':extra,'fstype':fstype,'mount_source':unescape(src),'superblock_options':fsopt}
                mounts.setdefault(devid,[]).append(mount)
        all_mounts=[]
        for devid,mnts in mounts.items():
            # Binding detection

            # Skip single mounts
            if len(mnts) <= 1:
                for mnt in mnts:
                    if mnt['mount_point'] not in [x['mount_point'] for x in all_mounts]:
                        # skip duplicated mount points
                        mnt.setdefault('is_binding', 'no')
                        all_mounts.append(mnt)
                continue
            # Sort list to get the first mount of the device's root dir (if still mounted)
            mnts.sort(key=lambda x: x['root'])
            src = mnts[0]
            src.setdefault('is_binding','no')
            all_mounts.append(src)
            binds = mnts[1:]
            for bindmount in binds:
                if src['root'] != bindmount['root']:
                    bindmount['mount_source'] = src['mount_point']+'/'+os.path.relpath(bindmount['root'],src['root'])
                elif src['fstype'] == 'cifs':
                    bindmount['mount_source'] = src['mount_point']
                elif src['fstype'] == 'nfs':
                    bindmount['mount_source'] = src['mount_point']+bindmount['mount_source'][len(src['mount_source']):]


                bindmount.setdefault('is_binding','yes')
                all_mounts.append(bindmount)
        #        print '{0} -> {1[mount_point]} ({1[mount_options]})'.format(src['mount_point'],bindmount)
        #for x in all_mounts:
        #    print '{mount_source} {mount_point} {fstype} {is_binding}'.format(**x)
        return all_mounts

    def get_mounts(self,*args,**kwargs):
        mounts=self.parse_self_mountinfo()
        #findmnt = json.loads(subprocess.check_output(['findmnt','-J'],stderr=open(os.devnull,'w')))
        #mounts = self.complete_binding_mapping(self.parse_findmnt(findmnt['filesystems']))
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

        mapping = {'PSEUDO': {'fstype':['sysfs','proc','devtmpfs','devpts','tmpfs','securityfs','cgroup','pstore','autofs','mqueue','debugfs','hugetlbfs','rpc_pipefs','fusectl','binfmt_misc','nfsd','gvfsd-fuse']},
                   'NETWORK':{'fstype':['nfs','cifs']},
                   'DISK':{'mount_source':['/dev/']},
                   'BIND':{'is_binding':['yes']} # 'B'ind is tested first, before 'D'isc
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

    def get_server_sync(self,*args,**kwargs):
        if not os.path.isdir('/net/server-sync'):
            return 'NO_EXIST'
        lst=self.execute(run='getfacl -tp -R /net/server-sync/').split('\n')
        regexp=re.compile('^#\sfile:\s/net/server-sync(\S+)')
        skip_search=False
        d={}

        def make_hierarchy(lkeys,value,d={}):
            if len(lkeys) == 0:
                return value
            elif len(lkeys) == 1:
                return d.setdefault(lkeys[0],value)
            else:
                return d.setdefault(lkeys[0],make_hierarchy(lkeys[1:],value,d[lkeys[0]]))

        attrs={}
        for line in lst:
            if line == '':
                lsplit=[li for li in skip_search.split('/') if li != '']
                if 'mask' in attrs:
                    attrs['acls']=True
                else:
                    attrs['acls']=False
                d.update(make_hierarchy(lsplit,attrs,d))
                skip_search=False
                attrs={}
                continue
            if skip_search:
                fields=[ field for field in line.split(' ') if field != '']
                attrs.setdefault('__'+fields[0],{})
                perms={}
                if fields[0] not in ['mask','other']:
                    skip_field=0
                else:
                    skip_field=1
                perms.setdefault('perms',fields[2-skip_field])
                try:
                    perms.setdefault('defaults',fields[3-skip_field])
                except:
                    perms.setdefault('defaults',None)

                attrs['__'+fields[0]].setdefault(fields[1],perms)
                #attrs[fields[0]][fields[1]].append(perms)

            else:
                m = re.findall(regexp,line)
                if m:
                    skip_search=m[0]
                    if os.path.isdir('/net/server-sync'+skip_search):
                        attrs['__is_dir']=True
                        attrs['__is_file']=False
                    else:
                        attrs['__is_dir']=False
                        attrs['__is_file']=True

        return d


    def run(self,*args,**kwargs):
        output = {'MOUNTS_INFO':None}
        output['MOUNTS_INFO']=self.get_mounts()
        output['RAW_MOUNTS_INFO']=self.compress_file(file='/proc/self/mounts')
        output['FSTAB']=self.uncomment('/etc/fstab')
        output['DISK_IDS']=self.execute(run='blkid',stderr=None)
        output['SERVER_SYNC_INFO']=self.get_server_sync()

        return output