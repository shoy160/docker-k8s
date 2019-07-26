# coding:utf-8

from handler.app import BaseHandler, app


@app.route('/')
class IndexHandler(BaseHandler):
    def get(self):
        self.render('index.html')


@app.route('/api/login')
class LoginHandler(BaseHandler):
    def post(self):
        ''' 登录
        '''
        account = self.get_argument('account', '')
        pwd = self.get_argument('password', '')
        if 'admin' != account:
            self.json_error('登录帐号不存在')
            return
        if 'icb@888' != pwd:
            self.json_error('登录密码不正确')
            return
        self.set_secure_cookie('username', account)
        self.json_success()

    def delete(self):
        ''' 退出登录
        '''
        self.clear_cookie('username')
        self.json_success()
