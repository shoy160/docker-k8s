# coding:utf-8
import json
from services.app import BaseHandler, app


@app.route('/api/login')
class LoginHandler(BaseHandler):

    def post(self):
        ''' 登录
        '''
        # try:
        #     data = json.loads(self.request.body)
        # except:
        #     pass
        # print(data)
        account = self.get_argument('account', '')
        pwd = self.get_argument('password', '')
        if 'admin' != account:
            self.json_error('登录帐号不存在')
            return
        if 'icb@888' != pwd:
            self.json_error('登录密码不正确')
            return
        self.set_secure_cookie('__registry_u', account)
        self.json_success()

    def delete(self):
        ''' 退出登录
        '''
        self.clear_cookie('__registry_u')
        self.json_success()
