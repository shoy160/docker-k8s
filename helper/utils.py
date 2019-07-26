# coding:utf-8

import traceback
import subprocess
import logging


def call_command(command):
    '''执行shell命令
    '''
    logger = logging.getLogger()
    try:
        out_bytes = subprocess.check_output(
            command, shell=True, timeout=2000, stderr=subprocess.STDOUT)
        return True, out_bytes.decode('gbk')
    except subprocess.CalledProcessError as ex:
        traceback.format_exc()
        logger.warn(ex.stdout.decode('gbk'))
        return False, ex.stdout.decode('gbk')
