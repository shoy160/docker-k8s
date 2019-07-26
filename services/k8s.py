# coding:utf-8

from helper.utils import call_command
from services.app import BaseHandler, app
from tornado.options import options


@app.route('/api/k8s/(.*)')
class K8sHandler(BaseHandler):
    def get(self, *args):
        ''' deploy当前运行的镜像版本
        '''
        deploy = args[0]
        ns = self.get_argument('ns', 'icb')
        image, tag = self.__deploy_image(deploy, ns)

        self.json_success({
            'deploy': deploy,
            'image': image,
            'tag': tag,
            'ns': ns
        })

    def __deploy_image(self, deploy, ns='icb'):
        ''' 获取当前运行的镜像
        '''
        command = "kubectl get deploy {0} -n {1} -o wide | awk '{print $7}' | awk -F '/' '{print $2}'".format(
            deploy, ns)
        status, msg = call_command(command)
        if status == False:
            return None, None
        image, tag = str.split(':', 1)
        if tag == '':
            tag = 'latest'
        return image, tag

    # 依赖kubectl
    def put(self, *args):
        ''' 滚动更新K8S
        :param  image:string    镜像名称
        :param  tag:string      标签名称,默认latest
        :param  ns:string       namespace,默认icb
        '''
        deploy = args[0]
        image = self.get_argument('image', deploy)
        tag = self.get_argument('tag', 'latest')
        ns = self.get_argument('ns', 'icb')

        c_image, c_tag = self.__deploy_image(deploy, ns)
        if c_image == None:
            self.json_error('deploy not exists')
            return

        if c_image == image and c_tag == tag:
            # 版本相同时
            command = 'kubectl delete rs -l app={0} -n {1}'.format(deploy, ns)
        else:
            # 版本不同时
            command = 'kubectl set image deployment {0} {1}={2}:{3} -n {4}'.format(
                deploy, deploy, image, tag, ns)

        self.logger.info(command)
        status, msg = call_command(command)
        if status:
            self.json_success(msg)
        else:
            self.json_error('更新K8S失败')
