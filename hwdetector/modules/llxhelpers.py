#!/usr/bin/env python
import hwdetector.Detector as Detector
import utils.log as log
import re
import urllib2 as urllib
import os.path
import grp,pwd
import subprocess,time

log.debug("File "+__name__+" loaded")

class LlxHelpers(Detector):
    _PROVIDES = ['HELPER_EXECUTE','HELPER_UNCOMMENT',"HELPER_GET_FILE_FROM_NET",'HELPER_FILE_FIND_LINE','HELPER_DEMOTE','HELPER_CHECK_ROOT','HELPER_WHO_I_AM','HELPER_USERS_LOGGED']
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
        try:
            is_file = os.path.isfile(args[0])
        except:
            is_file = False
        if is_file:
            #reg=re.compile('^\s*([^#].+$)')
            reg=re.compile(r'^(\s*|#.*)*$')
            with open(args[0],'r') as f:
                for line in f.readlines():
                    m=re.match(reg,line)
                    if not m:
                        r += line + "\n"
                    #m=re.match(reg,line)
                    #if m:
                    #    r = r + m.group(1) + "\n"
        else:
            if type(args[0]) == type(list()):
                string = ''.join(str(args[0]))
            else:
                string=str(args[0])
            #reg = re.compile('^\s*([^#].+$)')
            reg=re.compile(r'^(\s*|#.*)*$')
            for line in string.split("\n"):
                m=re.match(reg,line)
                if not m:
                    r += line + "\n"
                #m = re.match(reg, line)
                #if m:
                #    r = r + m.group(1) + "\n"
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

    def file_find_line(self,*args,**kwargs):

        if not (type(args[0]) == type(str()) or type(args[0]) == type(list())):
            return None

        is_file=os.path.isfile(args[0])

        multimatch = type(args[1]) == type(list())

        if not multimatch:
            keys = [ k.strip() for k in args[1:] if k and k.strip() ]
        else:
            keys = []
            for k_item in args[1]:
                if type(k_item) == type(list()):
                    keys.append([k.strip() for k in k_item if k and k.strip()])

        if not is_file:
            if type(args[0]) != type(list()):
                s = args[0].split("\n")
            else:
                s=args[0]
        else:
            with open(args[0],'r') as f:
                s=f.readlines()

        if not multimatch:
            r=re.compile('\s+'.join(keys),re.IGNORECASE)
        else:
            r=[]
            for k in keys:
                r.append(re.compile('\s+'.join(k),re.IGNORECASE))
        i=0
        output = []
        for line in s:
            if not multimatch:
                m=re.findall(r,line)
                if m:
                    return m
            else:
                m=[ test for test in [ re.findall(regexp,line) for regexp in r ] if test ]
                if m:
                    i = i+1
                    output.append(m[0])
                if i == len(r):
                    return output

        return None

    def demote(self,*args,**kwargs):
        try:
            if os.getuid() != 0:
                os.setuid(0)
            if os.getgid() != 0:
                os.setgid(0)
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
        params.setdefault('stdout',subprocess.PIPE)
        with_uncomment=False
        if 'nocomment' in kwargs:
            if kwargs['nocomment'] == True or kwargs['nocomment'] == 'yes':
                with_uncomment=True

        if 'asroot' in kwargs:
            if kwargs['asroot'] == True or kwargs['asroot'] == 'yes':
                params.setdefault('preexec_fn', self.demote)
        params.setdefault('shell',shell)
        stdout=None
        stderr=None
        try:
            start=time.time()
            p=subprocess.Popen(runlist,**params)
            while p.poll() is None and timeout_remaning > 0:
                time.sleep(delay)
                timeout_remaning -= delay
                stdout,stderr = p.communicate()
            if timeout_remaning <= 0:
                raise Exception('timeout({}) exceded while executing {}'.format(timeout,kwargs['run']))
        except Exception as e:
            log.error('Error executing: {}'.format(e))
            return None
        if stdout != None:
            if with_uncomment:
                return self.uncomment(stdout.strip())
            else:
                return stdout.strip()
        else:
            log.warning("Execution of {} hasn't produced any result, returning None")
            return None

    def run(self,*args,**kwargs):
        return {
            'HELPER_UNCOMMENT':{'code':self.uncomment,'glob':globals()},
            'HELPER_GET_FILE_FROM_NET': {'code': self.get_file_from_net, 'glob': globals()},
            'HELPER_FILE_FIND_LINE':{'code': self.file_find_line, 'glob': globals()},
            'HELPER_DEMOTE':{'code':self.demote,'glob':globals()},
            'HELPER_CHECK_ROOT':{'code':self.check_root,'glob':globals()},
            'HELPER_WHO_I_AM':{'code':self.who_i_am,'glob':globals()},
            'HELPER_EXECUTE':{'code':self.execute,'glob':globals()},
            'HELPER_USERS_LOGGED':{'code':self.users_logged,'glob':globals()}
                }