# coding:utf-8

import tornado.web
import tornado.options

from tornado.options import define, options
from handler import *
from handler.app import app

define("port", default=8080, help="run on the given port", type=int)
define("registry", default="http://192.168.0.231:5000",
       help="image registry address", type=str)
define("page-size", default=15, help="page size for list", type=int)


if __name__ == "__main__":
    # 转换命令行
    tornado.options.parse_command_line()
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    # http_server.bind(options.port)
    # http_server.start(2)
    print("listening on " + str(options.port))
    tornado.ioloop.IOLoop.instance().start()
