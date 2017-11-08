#!/usr/bin/env python
import hwdetector.Detector as Detector
import utils.log as log
import os

log.debug("File "+__name__+" loaded")

class LlxUsers(Detector):
    _NEEDS = ['HELPER_EXECUTE','HELPER_USERS_LOGGED','LDAP_INFO','MOUNTS_INFO','LLIUREX_SESSION_TYPE','LLIUREX_RELEASE','HELPER_WHO_I_AM','LOGIN_TYPE','LDAP_MODE','NFS_INITIALIZATION']
    _PROVIDES = ['USERS_INFO','USER_TEST']


    def check_mounts(self,username,typeuser,*args,**kwargs):
        mounts_info=kwargs['MOUNTS_INFO']
        session_type = kwargs['LLIUREX_SESSION_TYPE'].upper()
        release = kwargs['LLIUREX_RELEASE'].lower()
        ldap_mode = kwargs['LDAP_MODE'].lower()
        nfs_server = kwargs['NFS_INITIALIZATION']
        ret = None
        msg = []

        if release != 'server' and release != 'client':
            return (True,['Not in classroom model'])

        def check_mount_network(username,shares,mounts_info):
            msgs=[]
            ret = True
            for share in shares:
                mountpoint='/run/' + username + '/' + shares[share]
                mountsource='//server/'+share
                for x in mounts_info['NETWORK']:
                    ret = False
                    if x['mount_point'] ==  mountpoint and x['mount_source'] == mountsource and x['fstype'] == 'cifs':
                        ret = True
                        msg.append('Samba share {} mounted under {}'.format(mountsource,mountpoint))
                        break
                if not ret:
                    msgs.append('Samba share {} NOT mounted under {}'.format(mountsource,mountpoint))
                    break
                else:
                    ret = True
            return (ret,msgs)
        def check_binds(username,bind_paths,mounts_info,nfs_server):
            msgs = []
            ret = True
            for bind in bind_paths:
                for x in mounts_info['BIND']:
                    ret = False
                    if x['mount_point'].startswith('/home/' + username) and x['mount_source'] == bind_paths[bind]:
                        ret = True
                        msg.append('Bindmount {} from {} available'.format(x['mount_point'],bind_paths[bind]))
                        if nfs_server:
                            for x2 in mounts_info['NETWORK']:
                                ret2 = False
                                if x2['devid'] == x['devid'] and x2['mount_source'].startswith(nfs_server):
                                    ret2 = True
                                    msg.append('Referred share ({}) from bindmount ({}) is mounted from server ({})'.format(x2['mount_point'],x['mount_source'],nfs_server))
                                    break
                            if not ret2:
                                msg.append('Referred share ({}) from bindmount ({}) NOT mounted from server ({})'.format(x2['mount_point'],x['mount_source'],nfs_server))
                                ret = False
                                break
                        else:
                            ret2 = True
                            msg.append('Mounting from local without nfs, skipped checking')

                        break
                if not ret:
                    msg.append('Bindmount {} from {} NOT available'.format(bind,bind_paths[bind]))
                    break

            return (ret,msgs)

        samba_shares = []
        nfs_bind_paths = {}
        if typeuser == 'student':
            if release == 'server':
                nfs_bind_paths={'Desktop':'/net/server-sync/home/students/'+username+'/Desktop','Documents':'/net/server-sync/home/students/'+username+'/Documents','share':'/net/server-sync/share','groups_share':'/net/server-sync/groups_share'}
            elif release == 'client':
                if session_type != 'THIN':
                    samba_shares = {'home':'home','share':'share','groups_share':'groups_share'}
                nfs_bind_paths={'Desktop':'/run/'+username+'/home/students/'+username+'/Desktop','Documents':'/run/'+username+'/home/students/'+username+'/Documents','share':'/run/'+username+'/share','groups_share':'/run/'+username+'/groups_share'}
        elif typeuser == 'teacher':
            if release == 'server':
                nfs_bind_paths={'Desktop':'/net/server-sync/home/teachers/'+username+'/Desktop','Documents':'/net/server-sync/home/teachers/'+username+'/Documents','share':'/net/server-sync/share','groups_share':'/net/server-sync/groups_share','teachers_share':'/net/server-sync/teachers_share','/home/students':'/home/students'}
            elif release == 'client':
                if session_type != 'THIN':
                    samba_shares = {'home':'home','share':'share', 'groups_share':'groups_share', 'share_teachers':'teachers_share'}
                nfs_bind_paths={'Desktop':'/run/'+username+'/home/teachers/'+username+'/Desktop','Documents':'/run/'+username+'/home/teachers/'+username+'/Documents','share':'/run/'+username+'/share','groups_share':'/run/'+username+'/groups_share','teachers_share':'/run/'+username+'/teachers_share','/home/students':'/home/students'}
        elif typeuser == 'admin':
            if release == 'server':
                nfs_bind_paths={'Desktop':'/net/server-sync/home/admins/'+username+'/Desktop','Documents':'/net/server-sync/home/admins/'+username+'/Documents','share':'/net/server-sync/share','groups_share':'/net/server-sync/groups_share'}
            elif release == 'client':
                if session_type != 'THIN':
                    samba_shares = {'home':'home','share':'share','groups_share':'groups_share','share_teachers':'teachers_share'}
                nfs_bind_paths={'Desktop':'/run/'+username+'/home/admins/'+username+'/Desktop','Documents':'/run/'+username+'/home/admins/'+username+'/Documents','share':'/run/'+username+'/share','groups_share':'/run/'+username+'/groups_share'}

        ret, msgs = check_mount_network(username,samba_shares,mounts_info)
        msg.extend(msgs)
        if ret:
            ret,msgs=check_binds(username,nfs_bind_paths,mounts_info,nfs_server)
            msg.extend(msgs)

        return (ret,msg)

        # if release == 'client':
        #     if typeuser == 'student':
        #         if session_type == 'FAT' or session_type == 'SEMI':
        #             shares = ['home','share','groups_share']
        #             ret, msgs = check_mount_network(username,shares,mounts_info)
        #             msg.extend(msgs)
        #             # for share in ['home','share','groups_share']:
        #             #     mountpoint='/run/' + username + '/' + share
        #             #     mountsource='//server/'+share
        #             #     for x in mounts_info['NETWORK']:
        #             #         ret = False
        #             #         if x['mount_point'] ==  mountpoint and x['mount_source'] == mountsource and x['fstype'] == 'cifs':
        #             #             ret = True
        #             #             msg.append('Samba share {} mounted under {}'.format(mountsource,mountpoint))
        #             #             break
        #             #     if not ret:
        #             #         msg.append('Samba share {} not mounted under {}'.format(mountsource,mountpoint))
        #             #         break
        #             #     else:
        #             #         ret = True
        #             if ret:
        #                 bind_paths={'Desktop':'/run/'+username+'/home/students/'+username+'/Desktop','Documents':'/run/'+username+'/home/students/'+username+'/Documents','share':'/run/'+username+'/share','groups_share':'/run/'+username+'/groups_share'}
        #                 ret,msgs=check_binds(username,bind_paths,mounts_info)
        #                 msg.extend(msgs)
        #                 # for bind in bind_paths:
        #                 #     for x in mounts_info['BIND']:
        #                 #         ret = False
        #                 #         if x['mount_point'].startswith('/home/' + username) and x['mount_source'] == bind_paths[bind]:
        #                 #             ret = True
        #                 #             msg.append('Bindmount {} from {} available'.format(x['mount_point'],bind_paths[bind]))
        #                 #             break
        #                 #     if not ret:
        #                 #         msg.append('Bindmount {} from {} not available'.format(bind,bind_paths[bind]))
        #                 #         break
        #
        #         elif session_type == 'THIN':
        #             pass
        #     elif typeuser == 'teacher':
        #         pass
        #     elif typeuser == 'admin':
        #         pass
        # elif release == 'server':
        #     if typeuser == 'student':
        #         if session_type == 'FAT' or session_type == 'SEMI':
        #             bind_paths={'Desktop':'/net/server-sync/home/students/'+username+'/Desktop','Documents':'/net/server-sync/home/students/'+username+'/Documents','share':'/net/server-sync/share','groups_share':'/net/server-sync/groups_share'}
        #             ret,msgs = check_binds(username,bind_paths,mounts_info)
        #             # for bind in bind_paths:
        #             #     for x in mounts_info['BIND']:
        #             #         ret = False
        #             #         if x['mount_point'].startswith('/home/' + username) and x['mount_source'] == bind_paths[bind]:
        #             #             ret = True
        #             #             msg.append('Bindmount {} from {} available'.format(x['mount_point'],bind_paths[bind]))
        #             #             break
        #             #     if not ret:
        #             #         msg.append('Bindmount {} from {} not available'.format(bind,bind_paths[bind]))
        #             #         break
        #
        #         elif session_type == 'THIN':
        #             pass
        #     elif typeuser == 'teacher':
        #         pass
        #     elif typeuser == 'admin':
        #         pass
        # else: # pyme, infantil, desktop, music
        #     return (True,['Not in classroom model'])
        #return (ret,msg)

    def run(self,*args,**kwargs):
        output={}
        LDAP_INFO=kwargs['LDAP_INFO']
        logged_users=self.users_logged()
        myinfo=self.who_i_am()

        try:
            people=LDAP_INFO['CONFIG']['DB']['net']['lliurex']['ma5']['People']
            users=[(x,people['Students'][x]) for x in people['Students'].keys() if type(people['Students'][x]) == type(dict())]
            admins=[(x,people['Admins'][x]) for x in people['Admins'].keys() if type(people['Admins'][x]) == type(dict())]
            teachers=[(x,people['Teachers'][x]) for x in people['Teachers'].keys() if type(people['Teachers'][x]) == type(dict())]
        except Exception as e:
            people = None # NO LDAP ACCESS DO IT ONLY FOR ME
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
        perm_info=self.execute(run=cmd,stderr=None).split("\n")
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

                    if u in logged_users:
                        output[u]['MOUNTS_OK']=self.check_mounts(u,'student',**kwargs)
                    else:
                        output[u]['MOUNTS_OK']=(None,['NOT_LOGGED_IN'])
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
                            and perm_dirs[homedir]['group']['teachers'] == '---' \
                            and perm_dirs[homedir]['group']['admins'] == 'rwx' \
                            and perm_dirs[homedir]['other'] == '---'
                    except:
                        output[u]['PERM_OK']=False

                    if u in logged_users:
                        output[u]['MOUNTS_OK']=self.check_mounts(u,'teacher',**kwargs)
                    else:
                        output[u]['MOUNTS_OK']=(None,['NOT_LOGGED_IN'])

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

                    if u in logged_users:
                        output[u]['MOUNTS_OK']=self.check_mounts(u,'admin',**kwargs)
                    else:
                        output[u]['MOUNTS_OK']=(None,['NOT_LOGGED_IN'])

                else:
                    output[u]={'HAS_HOME': False}

        return {'USERS_INFO':perm_dirs,'USER_TEST':output}
