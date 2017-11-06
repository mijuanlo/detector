#!/usr/bin/env python
import hwdetector.Detector as Detector
import utils.log as log
import os
import subprocess

log.debug("File "+__name__+" loaded")

class LlxUsers(Detector):
    _NEEDS = ['LDAP_INFO','MOUNTS_INFO','LLIUREX_SESSION_TYPE','LLIUREX_RELEASE','HELPER_WHO_I_AM','LOGIN_TYPE']
    _PROVIDES = ['USERS_INFO','USER_TEST']


    def check_mounts(self,username,typeuser,*args,**kwargs):
        mounts_info=kwargs['MOUNTS_INFO']
        session_type = kwargs['LLIUREX_SESSION_TYPE']
        ret = None
        msg = []

        if typeuser == 'student':
            if session_type == 'FAT' or session_type == 'SEMI':
                for share in ['home','share','groups_share']:
                    mountpoint='/run/' + username + '/' + share
                    mountsource='//server/'+share
                    for x in mounts_info['NETWORK']:
                        ret = False
                        if x['mount_point'] ==  mountpoint and x['mount_source'] == mountsource and x['fstype'] == 'cifs':
                            ret = True
                            msg.append('Samba share {} mounted under {}'.format(mountsource,mountpoint))
                            break
                    if not ret:
                        msg.append('Samba share {} not mounted under {}'.format(mountsource,mountpoint))
                        break
                    else:
                        ret = True
                if ret:
                    bind_paths={'Desktop':'/run/'+username+'/home/students/'+username+'/Desktop','Documents':'/run/'+username+'/home/students/'+username+'/Documents','share':'/run/'+username+'/share','groups_share':'/run/'+username+'/groups_share'}
                    for bind in bind_paths:
                        for x in mounts_info['BIND']:
                            ret = False
                            if x['mount_point'].startswith('/home/' + username) and x['mount_source'] == bind_paths[bind]:
                                ret = True
                                msg.append('Bindmount {} from {} available'.format(x['mount_point'],bind_paths[bind]))
                                break
                        if not ret:
                            msg.append('Bindmount {} from {} not available'.format(bind,bind_paths[bind]))
                            break

            elif session_type == 'THIN':
                pass
        elif typeuser == 'teacher':
            pass
        elif typeuser == 'admin':
            pass
        return (ret,msg)

    def run(self,*args,**kwargs):
        output={}
        LDAP_INFO=kwargs['LDAP_INFO']

        try:
            people=LDAP_INFO['CONFIG']['DB']['net']['lliurex']['ma5']['People']
            users=[(x,people['Students'][x]) for x in people['Students'].keys() if type(people['Students'][x]) == type(dict())]
            admins=[(x,people['Admins'][x]) for x in people['Admins'].keys() if type(people['Admins'][x]) == type(dict())]
            teachers=[(x,people['Teachers'][x]) for x in people['Teachers'].keys() if type(people['Teachers'][x]) == type(dict())]
        except Exception as e:
            people = None # NO LDAP ACCESS DO IT ONLY FOR ME
            myinfo=self.who_i_am()
            fake_ldap_info=(myinfo['name'],{'homeDirectory':[myinfo['user_info'][5]],'uid':[myinfo['name']]})
            users=[]
            admins=[]
            teachers=[]
            if kwargs['LOGIN_TYPE'].lower() == 'ldap':
                if 'students' in myinfo['groups']:
                    users.append(fake_ldap_info)
                elif 'teachers' in myinfo['groups']:
                    teachers.append(fake_ldap_info)


        # USER TEST FUNCTIONALITY

        homes = ['/home/'+x for x in os.listdir('/home/')]
        cmd = ['getfacl','-tp'] + homes
        perm_info=subprocess.check_output(cmd,stderr=open(os.devnull,'w')).split("\n")
        perm_dirs={}
        i=-1
        file=None
        while i < len(perm_info)-1:
            i+=1
            line=perm_info[i]
            if line.startswith('#'):
                # complete previous if exists
                if file:
                    if perm_dirs[file]['group'] or perm_dirs[file]['user']:
                        perm_dirs[file]['USE_ACLS']=True
                    else:
                        perm_dirs[file]['USE_ACLS'] =False
                file=line[8:]
                perm_dirs[file]={'USER':{},'GROUP':{},'user':{},'group':{},'other':{},'mask':{}}
                continue
            if line != '':
                field=[ x for x in line.split(' ') if x != '']
                if field[0] in ['other','mask']:
                    perm_dirs[file][field[0]]=field[1]
                else:
                    perm_dirs[file][field[0]][field[1]]=field[2]
        if users:
            for (u,udata) in users:
                #TEST HOME
                if os.path.exists(udata['homeDirectory'][0]):
                    output[u] = {'HAS_HOME': True}

                    homedir=udata['homeDirectory'][0]
                    user=udata['uid'][0]

                    try:
                        output[u]['PERM_OK']=\
                            perm_dirs[homedir]['USER'][user] == 'rwx' \
                            and perm_dirs[homedir]['user'][user] == 'rwx' \
                            and perm_dirs[homedir]['GROUP']['nogroup'] == 'r-x' \
                            and perm_dirs[homedir]['group']['students'] == '---' \
                            and perm_dirs[homedir]['group']['teachers'] == 'rwx' \
                            and perm_dirs[homedir]['group']['admins'] == 'rwx' \
                            and perm_dirs[homedir]['other'] == '---'
                    except:
                        output[u]['PERM_OK']=False

                    output[u]['MOUNTS_OK']=self.check_mounts(u,'student',**kwargs)
                else:
                    output[u]={'HAS_HOME': False}

        # TEACHERS
        if teachers:
            for (u,udata) in teachers:
                #TEST HOME
                if os.path.exists(udata['homeDirectory'][0]):
                    output[u] = {'HAS_HOME': True}

                    homedir=udata['homeDirectory'][0]
                    user=udata['uid'][0]

                    try:
                        output[u]['PERM_OK']=\
                            perm_dirs[homedir]['USER'][user] == 'rwx' \
                            and perm_dirs[homedir]['user'][user] == 'rwx' \
                            and perm_dirs[homedir]['GROUP']['nogroup'] == 'r-x' \
                            and perm_dirs[homedir]['group']['students'] == '---' \
                            and perm_dirs[homedir]['group']['teachers'] == 'rwx' \
                            and perm_dirs[homedir]['group']['admins'] == 'rwx' \
                            and perm_dirs[homedir]['other'] == '---'
                    except:
                        output[u]['PERM_OK']=False

                else:
                    output[u]={'HAS_HOME': False}

        # ADMINS
        if admins:
            for (u,udata) in admins:
                #TEST HOME
                if os.path.exists(udata['homeDirectory'][0]):
                    output[u] = {'HAS_HOME': True}

                    homedir=udata['homeDirectory'][0]
                    user=udata['uid'][0]

                    try:
                        output[u]['PERM_OK']=\
                            perm_dirs[homedir]['USER'][user] == 'rwx' \
                            and perm_dirs[homedir]['user'][user] == 'rwx' \
                            and perm_dirs[homedir]['GROUP']['nogroup'] == 'r-x' \
                            and perm_dirs[homedir]['group']['students'] == '---' \
                            and perm_dirs[homedir]['group']['teachers'] == 'rwx' \
                            and perm_dirs[homedir]['group']['admins'] == 'rwx' \
                            and perm_dirs[homedir]['other'] == '---'
                    except:
                        output[u]['PERM_OK']=False

                else:
                    output[u]={'HAS_HOME': False}

        return {'USERS_INFO':perm_dirs,'USER_TEST':output}
