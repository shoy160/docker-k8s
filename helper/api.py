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
from tornado.httpclient import AsyncHTTPClient
from tornado.httpclient import HTTPRequest


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

    async def __get_api(self, api, headers={}):

        try:
            # s = requests.session()
            # s.keep_alive = False
            url = self.registry_url + api
            client = AsyncHTTPClient()
            req = HTTPRequest(url=url,
                              method='GET', headers=headers, validate_cert=False)
            resp = await client.fetch(req)
            return json.loads(resp.body)
            # result = s.get(url, verify=False, headers=headers).content.strip()
            # # print(result)
            # return json.loads(result)
        except Exception as e:
            traceback.print_exc()
            self.logger.warn(e)
            return None

    async def __image_list(self):
        api = "/v2/_catalog"
        result = await self.__get_api(api)
        return result.get("repositories")

    async def __tag_layers(self, image, tag):
        api = "/v2/{0}/manifests/{1}".format(image, tag)
        result = await self.__get_api(
            api, {'Accept': 'application/vnd.docker.distribution.manifest.v2+json'})
        return result.get('layers')

    async def __tag_size(self, image, tag):
        ''' 获取镜像大小
        '''
        layers = await self.__tag_layers(image, tag)
        size = 0
        for layer in layers:
            size += int(layer.get('size'))
        return len(layers), size

    async def __tag_detail(self, image, tag):
        ''' 获取镜像创建时间
        :param  image:string
        :param  tags:array
        '''
        api = "/v2/{0}/manifests/{1}".format(image, tag)
        result = await self.__get_api(api)
        topLayer = json.loads(result.get("history")[0].get("v1Compatibility"))
        id = topLayer.get('id')
        # 创建时间
        time = get_local_time(topLayer.get("created"))
        # 镜像层数 & 大小
        count, size = await self.__tag_size(image, tag)
        return {'id': id[0:11], 'name': tag, 'count': count, 'size': format_size(size), 'time': time}

    async def get_image_history(self, image, tag):
        api = "/v2/{0}/manifests/{1}".format(image, tag)
        result = await self.__get_api(api)
        history = []
        for item in result.get('history'):
            layer = json.loads(item.get('v1Compatibility'))
            id = layer.get('id')[0:11]
            cmd = layer.get('container_config').get('Cmd')[-1]
            replace_re = re.compile('^/bin/sh -c (#\(nop\)\s+)?')
            cmd = replace_re.sub('', cmd)
            replace_re = re.compile('\n')
            cmd = replace_re.sub('<br/>', cmd)
            replace_re = re.compile('\s{2,}')
            cmd = replace_re.sub(' ', cmd)
            time = get_local_time(layer.get("created"))
            history.append({
                'id': id,
                'cmd': cmd,
                'time': time
            })
        count, size = await self.__tag_size(image, tag)

        return {'size': format_size(size), 'count': count, 'history': history}

    async def get_images_tags(self, image):
        ''' 获取镜像Tags
        :param  image:string    镜像名称
        '''
        api = "/v2/" + image + "/tags/list"
        result = await self.__get_api(api)
        tags = result.get('tags', [])
        total = len(tags)
        tags_list = []
        for tag in tags:
            detail = await self.__tag_detail(image, tag)
            tags_list.append(detail)
        # print(tags_list)
        tags_list = sorted(
            tags_list, key=lambda k: k["time"], reverse=True)
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
            image_api = "/v2/" + image + "/tags/list"
            result = await self.__get_api(image_api)
            tags = result.get('tags', [])
            # tags_time = []
            # for tag in tags:
            #     tags_time.append(
            #         {"tag": tag, "time": self.__tag_time(image, tag)})
            # tags_time = sorted(
            #     tags_time, key=lambda k: k["time"], reverse=True)
            images_tags.setdefault(image, len(tags))
        return len(docker_images), images_tags
