# coding:utf-8
import logging
import tornado.web
import tornado.options
import tornado.httpserver
import tornado.ioloop

from tornado.options import define, options
import services.index
import services.image
import services.k8s
import services.view
from services.app import app
import platform
import signal

if platform.system() == "Windows":
    import asyncio
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
is_closing = False


define("port", default=8080, help="run on the given port", type=int)
define("registry-url", default="http://192.168.0.231:5000",
       help="image registry url", type=str)
define("registry", default="docker.dev:5000", help="image registry", type=str)
define("page-size", default=15, help="page size for list", type=int)
define("namespace", default="icb", help="K8S NameSpace", type=str)
define("enable-k8s", default=False, help="Allow K8S Manage", type=bool)
define("enable-delete", default=False, help="Allow Delete Image", type=bool)
define("root-account", default='root', help="Root Account", type=str)
define("root-pwd", default='docker-k8s', help="Root Password", type=str)


def signal_handler(signum, frame):
    global is_closing
    logging.info('exiting...')
    is_closing = True


def try_exit():
    global is_closing
    if is_closing:
        # clean up here
        tornado.ioloop.IOLoop.instance().stop()
        logging.info('exit success')


if __name__ == "__main__":
    # 转换命令行
    tornado.options.parse_command_line()
    signal.signal(signal.SIGINT, signal_handler)
    # app.preload()
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    # http_server.bind(options.port)
    logger = logging.getLogger('server')
    logger.info("listening on " + str(options.port))
    # tornado.ioloop.PeriodicCallback(f2s, 2000).start()
    tornado.ioloop.PeriodicCallback(try_exit, 100).start()
    tornado.ioloop.IOLoop.instance().start()
