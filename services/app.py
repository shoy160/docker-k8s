# coding:utf-8

import os
import logging
import tornado.web
from tornado.web import RequestHandler
from tornado.options import options
from tornado.escape import json_encode
from helper.api import RegistryApi


class RouterConfig(tornado.web.Application):
    """ 重置Tornado自带的路有对象 """

    def route(self, url):
        """
        :param url: URL地址
        :return: 注册路由关系对应表的装饰器
        """

        def register(handler):
            """
            :param handler: URL对应的Handler
            :return: Handler
            """
            self.add_handlers(".*$", [(url, handler)]
                              )  # URL和Handler对应关系添加到路由表中
            return handler

        return register


app = RouterConfig(
    handlers=[
        (r'/css/(.*)', tornado.web.StaticFileHandler, {'path': 'views/css'}),
        (r'/images/(.*)', tornado.web.StaticFileHandler,
         {'path': 'views/image'}),
        (r'/js/(.*)', tornado.web.StaticFileHandler, {'path': 'views/js'}),
    ],
    cookie_secret='ulb7bEIZmwpV23Df3',
    compress_response=True,
    template_path=os.path.join(os.path.dirname(__file__), "../views"),
    static_path=os.path.join(os.path.dirname(__file__), "../static")
)


class BaseHandler(RequestHandler):
    def __init__(self, application, request, **kwargs):
        if 'REGISTRY_URL' in os.environ:
            self.registry_url = os.environ['REGISTRY_URL']
        else:
            self.registry_url = options.registry_url
        if 'DOCKER_REGISTRY' in os.environ:
            self.registry = os.environ['DOCKER_REGISTRY']
        else:
            self.registry = options.registry

        self.registry_api = RegistryApi(self.registry_url)
        self.logger = logging.getLogger()
        return super().__init__(application, request, **kwargs)

    def data_received(self, chunk):
        pass

    def get_current_user(self):
        return self.get_secure_cookie("__registry_u")

    def get_login_url(self):
        return "/login"

    def json_success(self, json=None):
        result = {
            'status': True,
            'code': 0,
            'message': '',
            'data': json
        }
        self.set_header('Content-Type', 'application/json')
        self.finish(result)

    def json_error(self, message, code=-1):
        result = {
            'status': False,
            'code': code,
            'message': message
        }
        self.set_header('Content-Type', 'application/json')
        self.set_status(500)
        self.finish(result)
