# coding:utf-8
import logging
from helper.utils import call_command

logger = logging.getLogger('k8s')

def get_deploy_image(deploy, ns='icb'):
    ''' 获取当前运行的镜像
    '''
    # return 'docker.dev:5000/spear:1.1.1'
    command = "kubectl get deploy %s -n %s -o wide | awk '{if (NR>1){print $7}}'" % (deploy, ns)        
    status, image = call_command(command)    
    logger.info('get deploy:%s,%s => %s,%s' % (deploy, ns, status, image))
    if not status or image == '' or image.startswith('error') or image.startswith('Error'):
        return None
    image = image.replace('\n', '')
    return image
