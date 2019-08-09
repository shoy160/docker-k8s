# coding:utf-8
import logging
import tornado.web
import tornado.options

from tornado.options import define, options
import services.index
import services.image
import services.k8s
import services.view
from services.app import app

define("port", default=8080, help="run on the given port", type=int)
define("registry-url", default="http://192.168.0.231:5000",
       help="image registry url", type=str)
define("registry", default="docker.dev:5000", help="image registry", type=str)
define("page-size", default=15, help="page size for list", type=int)
define("namespace", default="icb", help="K8S NameSpace", type=str)
define("enable-k8s", default=False, help="Allow K8S Manage", type=bool)
define("enable-delete", default=False, help="Allow Delete Image", type=bool)


if __name__ == "__main__":
    print('micro-market'.split('/')[-1])
#     # 转换命令行
#     tornado.options.parse_command_line()
#     http_server = tornado.httpserver.HTTPServer(app)
#     http_server.listen(options.port)
#     # http_server.bind(options.port)
#     # http_server.start(2)
#     logger = logging.getLogger('server')
#     logger.info("listening on " + str(options.port))
#     tornado.ioloop.IOLoop.instance().start()
