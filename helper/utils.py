# coding:utf-8
import json
import os
import time
import traceback
import subprocess
import logging
import math

__size_unit = 1000
__size_suffixes = 'KMGTPE'
logger = logging.getLogger('utils')


def call_command(command):
    '''执行shell命令
    '''
    logger.info(command)
    try:
        out_bytes = subprocess.check_output(
            command, shell=True, timeout=2000, stderr=subprocess.STDOUT)
        return True, out_bytes.decode('gbk')
    except subprocess.CalledProcessError as ex:
        traceback.format_exc()
        logger.warn('called command error:%s' % ex.stdout.decode('gbk'))
        return False, ex.stdout.decode('gbk')


def format_size(bytes_size):
    ''' 格式化文件大小
    '''
    if bytes_size < __size_unit:
        return '%dB' % bytes_size
    exp = int(math.log(float(bytes_size))/math.log(__size_unit))
    pre = __size_suffixes[exp-1:exp]
    size = math.pow(__size_unit, exp)
    if exp > 1:
        return '%.1f %sB' % (bytes_size / size, pre)
    else:
        return '%.0f %sB' % (bytes_size / size, pre)


def get_version(deploy, path='version.json'):
    versions = None
    if os.path.exists(path):
        with open(path, 'r+') as f:
            versions = json.load(f)
    if versions == None or deploy not in versions:
        return None
    return versions[deploy]


def set_version(deploy, image, tag, path='version.json'):
    versions = None
    if os.path.exists(path):
        with open(path, 'r+') as f:
            versions = json.load(f)
    if versions == None:
        versions = {}
    versions[deploy] = {
        'image': image,
        'tag': tag,
        'time': time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    }
    with open(path, 'w+') as f:
        t = json.dumps(versions, indent=4, sort_keys=True)
        f.write(t)
