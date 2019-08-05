# coding:utf-8

from helper.utils import call_command, set_version
from helper.k8s import get_deploy_image
from services.app import BaseHandler, app
import tornado.web
from tornado.options import options


@app.route('/api/k8s/(.*)')
class K8sHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self, *args):
        ''' deploy当前运行的镜像版本
        '''
        if not options.enable_k8s:
            self.json_error('k8s plugin is disabled')
            return
        deploy = args[0]
        ns = self.get_argument('ns', options.namespace)
        image = get_deploy_image(deploy, ns)

        self.json_success({
            'deploy': deploy,
            'image': image,
            'ns': ns
        })

    # 依赖kubectl
    @tornado.web.authenticated
    def put(self, *args):
        ''' 滚动更新K8S
        :param  image:string    镜像名称
        :param  tag:string      标签名称,默认latest
        :param  ns:string       namespace,默认icb
        '''
        if not options.enable_k8s:
            self.json_error('k8s plugin is disabled')
            return
        deploy = args[0]
        image = self.get_argument('image', deploy)
        tag = self.get_argument('tag', '')
        ns = self.get_argument('ns', options.namespace)

        # self.json_success({
        #     'deploy': deploy,
        #     'image': image,
        #     'tag': tag,
        #     'ns': ns
        # })

        c_image = get_deploy_image(deploy, ns)
        if c_image == None:
            self.json_error('deploy not exists')
            return
        t_image = "{0}/{1}".format(self.registry, image)
        if tag != '' and tag != 'latest':
            t_image += ":%s" % tag
        if c_image == t_image:
            # 版本相同时
            command = 'kubectl delete rs -l app={0} -n {1}'.format(deploy, ns)
        else:
            # 版本不同时
            command = 'kubectl set image deployment {0} {1}={2} -n {3}'.format(
                deploy, deploy, t_image, ns)
        status, msg = call_command(command)
        if status:
            self.json_success(msg)
            set_version(deploy, image, tag)
        else:
            self.json_error('更新K8S失败')
