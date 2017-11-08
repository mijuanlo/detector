#!/usr/bin/env python
import hwdetector.Detector as Detector
import utils.log as log

log.debug("File "+__name__+" loaded")

class LlxUsersTest(Detector):
    _NEEDS=['MOUNTS_INFO','USER_TEST']
    _PROVIDES=['LLXUSERS_TEST']

    def run(self,*args,**kwargs):
        status=True
        msg=[]
        msg_debug=[]
        mounts_info=kwargs['MOUNTS_INFO']
        user_test=kwargs['USER_TEST']
        for u in sorted(user_test.iterkeys()):
            if user_test[u]['HAS_HOME']:
                msg_debug.append('\n{}\n'.format(u.upper()))
                for k in user_test[u]:
                    if k != 'MOUNTS_OK':
                        msg_debug.append('{} {}\n'.format(k,user_test[u][k]))
                        if user_test[u][k] == False:
                            msg_debug.append('Home of user {} has wrong permission or owners\n'.format(u))
                            msg.append('Home of user {} has wrong permission or owners\n'.format(u))
                            status = False
                    else:
                        msg_debug.append('{} {}\nMESSAGES:\n{}\n'.format(k,user_test[u][k][0],'\n'.join(user_test[u][k][1])))
                        if user_test[u][k][0] == False:
                            msg.append('User {} have wrong mounts, detection says:\n{}\n'.format(u,'\n'.join(user_test[u][k][1])))
                            status = False
        msg=''.join(msg)
        msg_debug=''.join(msg_debug)
        return {'LLXUSERS_TEST':{'status':status,'msg':msg}}