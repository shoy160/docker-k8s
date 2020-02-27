# coding:utf-8

import re
import requests
import json
import math
import traceback
import logging
from dateutil.tz import tz
from datetime import datetime
from helper.utils import format_size
from tornado.httpclient import AsyncHTTPClient, HTTPRequest
from helper.cache import CacheHelper


def get_normal_time(time):
    h, t = time.split('T')
    t = t.split('.')[0]
    return h + " " + t


def get_local_time(time):
    from_zone = tz.gettz('UTC')
    to_zone = tz.gettz('CST')
    utc = datetime.strptime(get_normal_time(time), '%Y-%m-%d %H:%M:%S')
    utc = utc.replace(tzinfo=from_zone)
    local = utc.astimezone(to_zone)
    return datetime.strftime(local, "%Y-%m-%d %H:%M:%S")


class RegistryApi(object):

    def __init__(self, registry_url):
        self.registry_url = registry_url
        self.logger = logging.getLogger()
        self.logger.setLevel(logging.DEBUG)
        self.cache = CacheHelper('registry')

    async def __get_api(self, api, headers={}):

        try:
            url = self.registry_url + api
            self.logger.debug("request url:%s" % url)
            client = AsyncHTTPClient()
            req = HTTPRequest(url=url,
                              method='GET', headers=headers, validate_cert=False)
            resp = await client.fetch(req)
            return json.loads(resp.body)
        except Exception as e:
            traceback.print_exc()
            self.logger.warn(e)
            return None

    async def __image_list(self):
        ''' 镜像列表
        '''
        api = "/v2/_catalog"
        result = await self.__get_api(api)
        return result.get("repositories")

    async def __tag_list(self, image):
        ''' 标签列表
        '''
        api = "/v2/%s/tags/list" % image
        result = await self.__get_api(api)
        return result.get('tags', [])

    async def __tag_manifest(self, image, tag):
        api = "/v2/{0}/manifests/{1}".format(image, tag)
        result = await self.__get_api(api)
        return {
            'layers': result.get('fsLayers'),
            'history': result.get('history')
        }

    async def __tag_layers(self, image, tag):
        ''' 标签 层级
        '''
        key = "layers:%s:%s" % (image, tag)
        if self.cache.has(key):
            return self.cache.get(key)
        api = "/v2/{0}/manifests/{1}".format(image, tag)
        result = await self.__get_api(
            api, {'Accept': 'application/vnd.docker.distribution.manifest.v2+json'})
        layers = result.get('layers')
        data = {}
        total = 0
        for layer in layers:
            size = int(layer.get('size'))
            total += size
            data[layer.get('digest')] = size
        tag_layers = {
            'size': total,
            'list': data
        }
        self.cache.set(key, tag_layers)
        return tag_layers

    async def __tag_time(self, image, tag):
        ''' 标签时间
        '''
        key = "%s:%s" % (image, tag)
        if self.cache.has(key):
            return self.cache.get(key)
        result = await self.__tag_manifest(image, tag)
        topLayer = json.loads(result.get("history")[0].get("v1Compatibility"))
        # 创建时间
        time = get_local_time(topLayer.get("created"))
        tag_time = {
            'id': topLayer.get('id'),
            'time': time
        }
        self.cache.set(key, tag_time)
        return tag_time

    async def __image_time(self, image):
        ''' 镜像时间
        '''

        if self.cache.has(image):
            return self.cache.get(image)
        tags = await self.__tag_list(image)
        if len(tags) <= 0:
            return None
        tag_times = []
        for tag in tags:
            time = await self.__tag_time(image, tag)
            tag_times.append({
                'tag': tag,
                'time': time['time']
            })
        tag_times = sorted(
            tag_times, key=lambda k: k["time"], reverse=True)
        tag_time = tag_times[0]
        tag_time['count'] = len(tags)
        self.cache.set(image, tag_time)
        return tag_time

    async def __tag_detail(self, image, tag):
        ''' 获取镜像创建时间
        :param  image:string
        :param  tags:array
        '''
        tag_time = await self.__tag_time(image, tag)
        id = tag_time['id']
        time = tag_time['time']
        # 镜像层数 & 大小
        layers = await self.__tag_layers(image, tag)
        return {'id': id[0:11], 'name': tag, 'count': len(layers['list']), 'size': format_size(layers['size']), 'time': time}

    async def get_image_history(self, image, tag):
        result = await self.__tag_manifest(image, tag)
        layers = await self.__tag_layers(image, tag)

        history = []
        fs_layers = result.get('layers')
        history_list = result.get('history')
        length = len(history_list)
        for i in range(length):
            item = history_list[i]
            layer = json.loads(item.get('v1Compatibility'))
            id = layer.get('id')[0:11]
            cmd = layer.get('container_config').get('Cmd')[-1]
            replace_re = re.compile('^/bin/sh -c (#\(nop\)\s+)?')
            cmd = replace_re.sub('', cmd)
            replace_re = re.compile('\n')
            cmd = replace_re.sub('<br/>', cmd)
            # replace_re = re.compile('\s{2,}')
            # cmd = replace_re.sub(' ', cmd)
            # cmd = cmd.replace('&&', '&&<br/>')
            time = get_local_time(layer.get("created"))
            item = {
                'id': id,
                'cmd': cmd,
                'time': time,
                'size': '0B'
            }
            fs_layer = fs_layers[i]
            if fs_layer.get('blobSum') in layers['list']:
                item['size'] = format_size(layers[fs_layer.get('blobSum')])
            history.append(item)

        return {'size': format_size(layers['size']), 'count': len(layers), 'history': history}

    async def get_images_tags(self, image, page=1, size=10):
        ''' 获取镜像Tags
        :param  image:string    镜像名称
        '''
        tags = await self.__tag_list(image)
        total = len(tags)
        tag_times = []
        for tag in tags:
            time = await self.__tag_time(image, tag)
            tag_times.append({
                'tag': tag,
                'time': time['time']
            })
        tag_times = sorted(
            tag_times, key=lambda k: k["time"], reverse=True)
        tags_list = []
        # 分页
        start = (page-1)*size
        for item in tag_times[start:start + size]:
            detail = await self.__tag_detail(image, item['tag'])
            tags_list.append(detail)
        return total, tags_list

    async def get_images(self, page=1, size=15, keyword=''):
        ''' 获取镜像分页列表
        '''
        docker_images = await self.__image_list()
        images_tags = {}
        start = (page-1)*size
        if keyword != '':
            item_list = docker_images
            docker_images = []
            for image in item_list:
                if keyword not in image:
                    continue
                docker_images.append(image)
        for image in docker_images[start:start + size]:
            tags = await self.__image_time(image)
            images_tags.setdefault(image, tags)
        return len(docker_images), images_tags
