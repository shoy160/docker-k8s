# coding:utf-8

import os
import json
from services.app import BaseHandler, app
from tornado.options import options


@app.route('/api/login')
class LoginHandler(BaseHandler):

    def initialize(self):
        if 'ROOT_ACCOUNT' in os.environ:
            self.root_account = os.environ["ROOT_ACCOUNT"]
        else:
            self.root_account = options.root_account
        if 'ROOT_PWD' in os.environ:
            self.root_pwd = os.environ["ROOT_PWD"]
        else:
            self.root_pwd = options.root_pwd

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
        if self.root_account != account:
            self.json_error('登录帐号不存在')
            return
        if self.root_pwd != pwd:
            self.json_error('登录密码不正确')
            return
        self.set_secure_cookie('__registry_u', account)
        self.json_success()

    def delete(self):
        ''' 退出登录
        '''
        self.clear_cookie('__registry_u')
        self.json_success()
