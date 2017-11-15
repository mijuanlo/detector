#!/usr/bin/env python
import hwdetector.Detector as Detector
import utils.log as log

log.debug("File "+__name__+" loaded")

class LlxUsersTest(Detector):
    _NEEDS=['MOUNTS_INFO','USER_TEST']
    _PROVIDES=['LLXUSERS_TEST']

    def make_result(self,*args,**kwargs):
        ret=''
        if not ('result' in kwargs and 'msg' in kwargs):
            return
        if type(kwargs['result']) == type(list()):
            result=kwargs['result']
        else:
            result=[str(kwargs['result'])]

        for x in result:
            ret+='{}> {}: {}\n'.format(self.__class__.__name__,x,kwargs['msg'])
        return ret

    def run(self,*args,**kwargs):
        msg=[]
        status = False
        msg_debug=[]
        mounts_info=kwargs['MOUNTS_INFO']
        user_test=kwargs['USER_TEST']
        for u in sorted(user_test.iterkeys()):
            status=True
            if user_test[u]['HAS_HOME']:
                msg_debug.append('\n{}\n'.format(u.upper()))
                for k in user_test[u]:
                    if k != 'MOUNTS_OK':
                        msg_debug.append('{} {}\n'.format(k,user_test[u][k]))
                        if user_test[u][k] == False:
                            msg_debug.append('Home of user {} has wrong permission,owners or acl\'s\n'.format(u))
                            msg.append(self.make_result(result=['Home of user {} has wrong permission,owners or acl\'s'.format(u)],msg='Nok !'))
                            status = False
                    else:
                        msg_debug.append('{} {}\nMESSAGES:\n{}\n'.format(k,user_test[u][k][0],'\n'.join(user_test[u][k][1])))
                        if user_test[u][k][0] == False:
                            msg.append(self.make_result(result=['User {} has wrong mounts, detection says'.format(u)],msg=''))
                            msg.append(self.make_result(result=user_test[u]['MOUNTS_OK'][1],msg=''))
                            status = False
                if status:
                    msg.append(self.make_result(result=['Home of user {} seems with good permission,owners and acl\'s'.format(u)],msg='Ok!'))
                if 'NOT_LOGGED_IN' in user_test[u]['MOUNTS_OK'][1]:
                    msg.append(self.make_result(result='User {} not logged in, so i can\'t expect to analyze any mounts'.format(u),msg=''))
                else:
                    msg.append(self.make_result(result=['User {} has correct mounts, detection says'.format(u)],msg=''))
                    msg.append(self.make_result(result=user_test[u]['MOUNTS_OK'][1],msg='Ok!'))

        msg=''.join(msg)
        msg_debug=''.join(msg_debug)
        log.debug(msg_debug)
        return {'LLXUSERS_TEST':{'status':status,'msg':msg}}