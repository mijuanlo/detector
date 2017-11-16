#!/usr/bin/env python
import hwdetector.Detector as Detector
import utils.log as log
import re
import urllib2 as urllib
import os.path
import grp,pwd
import subprocess,time
import base64,zlib

log.debug("File "+__name__+" loaded")

class LlxHelpers(Detector):
    _PROVIDES = ['HELPER_EXECUTE','HELPER_UNCOMMENT',"HELPER_GET_FILE_FROM_NET",'HELPER_FILE_FIND_LINE','HELPER_DEMOTE','HELPER_SET_ROOT_IDS','HELPER_CHECK_ROOT','HELPER_WHO_I_AM','HELPER_USERS_LOGGED','ROOT_MODE','HELPER_COMPRESS_FILE','HELPER_LIST_FILES','HELPER_COMPACT_FILES']
    _NEEDS = []

    # def _close_stderr(self):
    #     self.errfile=os.fdopen(2,'w',0)
    #     sys.stderr.close()
    #     sys.stderr = open(os.devnull, 'w')
    #
    #
    # def _open_stderr(self):
    #     sys.stderr.flush()
    #     sys.stderr.close()
    #     sys.stderr = self.errfile
    #
    # def ctl_stderr(self,*args,**kwargs):
    #     keys=[k.lower() for k in kwargs.keys()]
    #     if 'close' in keys:
    #         self._close_stderr()
    #     if 'open' in keys:
    #         self._open_stderr()

    def uncomment(self,*args,**kwargs):
        r = ''
        comments=kwargs.get('comments',['#'])
        creg=[]
        for c in comments:
            creg.append(c+'.*')
        creg='|'.join(creg)
        try:
            is_file = os.path.isfile(args[0])
        except:
            is_file = False
        if is_file:
            reg=re.compile(r'^(\s*|{})*$'.format(creg))
            with open(args[0],'r') as f:
                for line in f.readlines():
                    m=re.match(reg,line)
                    if not m:
                        r += line

        else:
            if type(args[0]) == type(list()):
                string = ''.join(str(args[0]))
            else:
                string=str(args[0])

            reg=re.compile(r'^(\s*|#.*)*$')
            for line in string.split("\n"):
                m=re.match(reg,line)
                if not m:
                    r += line + "\n"
        return r.strip()

    def get_file_from_net(self,*args,**kwargs):
        if not args[0]:
            return None
        if 'proxy' in kwargs and kwargs['proxy'] == True:
            proxy = urllib.ProxyHandler() #use autodetected proxies
            opener = urllib.build_opener(proxy)
            urllib.install_opener(opener)

        proto=args[0].split(':')
        if proto[0]:
            proto=proto[0].lower()
        else:
            return None
        if 'http' != proto and 'https' != proto:
            return None
        try:
            content = urllib.urlopen(args[0])
            data = content.read()
            return data
        except Exception as e:
            return None

    def file_find_line(self, content, *args, **kwargs):

        if not (isinstance(content,str) or isinstance(content,list)):
            return None

        is_file=os.path.isfile(content)

        multimatch = isinstance(args[0],list)

        if not multimatch:
            keys = [k.strip() for k in args if k]
        else:
            keys = []
            for k_item in args[0]:
                if isinstance(k_item,list):
                    keys.append([k.strip() for k in k_item if k])

        if not is_file:
            if not isinstance(content,list):
                s = content.split("\n")
            else:
                s = content
        else:
            with open(content,'r') as f:
                s=f.readlines()

        if not multimatch:
            r=re.compile('\s*'.join(keys),re.IGNORECASE)
        else:
            r=[]
            for k in keys:
                r.append(re.compile('\s*'.join(k),re.IGNORECASE))
        i=0
        output = []
        for line in s:
            if not multimatch:
                m=re.findall(r,line)
                if m:
                    if kwargs.get('multiple_result',False):
                        output.append(m)
                    else:
                        return m
            else:
                m=[ test for test in [ re.findall(regexp,line) for regexp in r ] if test ]
                if m:
                    i = i+1
                    output.append(m[0])
                if i == len(r):
                    if kwargs.get('multiple_result',False):
                        output.append(m[0])
                    else:
                        return output

        return output

    def demote(self,*args,**kwargs):
        try:
            info=pwd.getpwnam('nobody')
            id=info.pw_uid
            gid=info.pw_gid
            os.setuid(id)
            os.setgid(gid)
        except Exception as e:
            return False
        return True
    def set_root_ids(self,*args,**kwargs):
        try:
            os.seteuid(0)
            os.setegid(0)
        except Exception as e:
            return False
        return True
    def check_root(self,*args,**kwargs):
        if os.geteuid() == 0:
            return True
        else:
            return False

    def who_i_am(self,*args,**kwargs):
        euid=os.geteuid()
        user_info=pwd.getpwuid(euid)
        user_name=user_info[0]
        groups = [group[0] for group in grp.getgrall() if user_name in group[3]]
        return {'id':euid,'user_info':user_info,'name':user_name,'groups':groups}

    def users_logged(self,*args,**kwargs):
        l=[]
        regexp=re.compile(r'^(?P<username>\S+)\s+(?P<terminal>\S+)\s+\S+\s+\S+\s+(?P<display>\S+)?$')
        for line in self.execute(run='who').split('\n'):
            m = re.match(regexp,line)
            if m:
                d=m.groupdict()
                if d['display'] != None and d['username'] not in l:
                    l.append(d['username'])
        return l

    def execute(self,timeout=3.0,shell=False,*args,**kwargs):
        params={}
        if 'run' not in kwargs:
            log.error('Execute called without \'run\' key parameter')
            return None
        else:
            if type(kwargs['run']) != type(list()):
                runlist=kwargs['run'].split(' ')
            else:
                runlist=kwargs['run']
        timeout_remaning=float(timeout)
        #Ready for python3
        #params.setdefault('timeout',int(timeout))
        #Python 2 code
        delay=0.1
        if 'stderr' in kwargs:
            if kwargs['stderr'] == 'stdout':
                params.setdefault('stderr',subprocess.STDOUT)
            if kwargs['stderr'] == None or kwargs['stderr'] == 'no':
                params.setdefault('stderr',open(os.devnull,'w'))
            else:
                params.setdefault('stderr',subprocess.PIPE)
        else:
            params.setdefault('stderr',subprocess.PIPE)
        params.setdefault('stdout',subprocess.PIPE)
        with_uncomment=False
        if 'nocomment' in kwargs:
            if kwargs['nocomment'] == True or kwargs['nocomment'] == 'yes':
                with_uncomment=True

        myinfo=pwd.getpwuid(os.geteuid())
        user = myinfo.pw_name
        group = grp.getgrgid(myinfo.pw_gid).gr_name
        root_mode = False
        if self.check_root():
            if 'asroot' in kwargs:
                if kwargs['asroot'] == True or kwargs['asroot'] == 'yes':
                    root_mode=True
            if not root_mode:
                params.setdefault('preexec_fn', self.demote)
                user = 'nobody'
                group = 'nogroup'
            else:
                params.setdefault('preexec_fn', self.set_root_ids)

        params.setdefault('shell',shell)
        stdout=None
        stderr=None
        log.info('Executing command \'{}\' as {}:{}'.format(' '.join(runlist),user,group))
        try:
            start=time.time()
            p=subprocess.Popen(runlist,**params)
            ret=p.poll()
            while ret is None and timeout_remaning > 0:
                time.sleep(delay)
                timeout_remaning -= delay
                stdout,stderr = p.communicate()
                ret = p.poll()
            if stdout is None:
                stdout,stderr = p.communicate()
            if timeout_remaning <= 0:
                raise Exception('timeout({}) exceded while executing {}'.format(timeout,kwargs['run']))
            if ret != 0:
                if stderr != '':
                    stderr = 'stderr={}'.format(stderr)
                log.warning('Execution with exit code {} (possible error) {}'.format(ret,stderr))
        except Exception as e:
            log.error('Error executing: {}'.format(e))
            return None
        if stdout != None:
            if with_uncomment:
                return self.uncomment(stdout.strip())
            else:
                return stdout.strip()
        else:
            log.error("Execution of {} hasn't produced any result, returning None".format(kwargs['run']))
            return None
    def compress_file(self,*args,**kwargs):
        file=kwargs.get('file')
        string=kwargs.get('string')
        if not ('file' in kwargs or  'string' in kwargs):
            log.error('Compressing called without \'file\' or \'string\' keyparam')
        if file:
            if os.path.exists(file):
                try:
                    with open(file,'r') as f:
                        return ('__gz__',base64.b64encode(zlib.compress(f.read().strip())))
                except Exception as e:
                    return 'NOT_READABLE'
        if string:
            try:
                return ('__gz__',base64.b64encode(zlib.compress(string.strip())))
            except Exception as e:
                raise Exception(e)

    def list_files(self,*args,**kwargs):
        path=kwargs.get('path')
        filter=kwargs.get('filter')
        regexp=kwargs.get('regexp')

        if not path:
            log.error('List files called without \'path\' keyparameter')
            return None

        paths=[]
        if type(path) == type(str()):
            paths.append(path)
        elif type(path) == type(list()):
            for x in [ x for x in path if type(x) == type(str()) ]:
                paths.append(x)
        else:
            return None

        paths=[x for x in paths if os.path.exists(x)]

        if regexp:
            reg=re.compile(regexp)
            filter=lambda x: [ f for f in x if re.match(reg,f)]

        files=[]

        for p in paths:
            if os.path.isdir(p):
                for root,dirnames,filenames in os.walk(p):
                    if filter:
                        for filename in filter(filenames):
                            files.append(os.path.join(root,filename))
                    else:
                        for filename in filenames:
                            files.append(os.path.join(root,filename))
            else:
                files.append(p)
        return files

    def compact_files(self,*args,**kwargs):
        files=self.list_files(*args,**kwargs)
        if not (files and type(files) == type(list())):
            return None
        content=''
        for file in files:
            try:
                with open(file,'r') as f:
                    content+=f.read()
            except Exception as e:
                pass

        return self.uncomment(content)

    def run(self,*args,**kwargs):
        return {
            'ROOT_MODE': self.check_root(),
            'HELPER_UNCOMMENT':{'code':self.uncomment,'glob':globals()},
            'HELPER_GET_FILE_FROM_NET': {'code': self.get_file_from_net, 'glob': globals()},
            'HELPER_FILE_FIND_LINE':{'code': self.file_find_line, 'glob': globals()},
            'HELPER_DEMOTE':{'code':self.demote,'glob':globals()},
            'HELPER_SET_ROOT_IDS':{'code':self.set_root_ids,'glob':globals()},
            'HELPER_CHECK_ROOT':{'code':self.check_root,'glob':globals()},
            'HELPER_WHO_I_AM':{'code':self.who_i_am,'glob':globals()},
            'HELPER_EXECUTE':{'code':self.execute,'glob':globals()},
            'HELPER_USERS_LOGGED':{'code':self.users_logged,'glob':globals()},
            'HELPER_COMPRESS_FILE':{'code':self.compress_file,'glob':globals()},
            'HELPER_COMPACT_FILES':{'code':self.compact_files,'glob':globals()},
            'HELPER_LIST_FILES':{'code':self.list_files,'glob':globals()}
                }