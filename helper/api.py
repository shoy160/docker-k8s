# coding:utf-8

import requests
import json
import math
import traceback
from dateutil.tz import tz
from datetime import datetime


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

    def __get_api(self, api):
        try:
            s = requests.session()
            s.keep_alive = False
            url = self.registry_url + api
            result = s.get(url, verify=False).content.strip()
            # print(result)
            return json.loads(result)
        except Exception as e:
            traceback.print_exc()
            self.logger.warn(e)
            return None

    def __image_list(self):
        api = "/v2/_catalog"
        result = self.__get_api(api)
        return result.get("repositories")

    def __tag_time(self, image, tag):
        ''' 获取镜像创建时间
        :param  image:string
        :param  tags:array
        '''
        api = "/v2/" + image + "/manifests/" + tag
        result = self.__get_api(api)
        time = get_local_time(
            json.loads(result.get("history")[0].get("v1Compatibility")).get("created"))
        return time

    def get_images_tags(self, image):
        ''' 获取镜像Tags
        :param  image:string    镜像名称
        '''
        api = "/v2/" + image + "/tags/list"
        tags = self.__get_api(api).get('tags', [])
        tags_time = []
        for tag in tags:
            tags_time.append(
                {"tag": tag, "time": self.__tag_time(image, tag)})
        tags_time = sorted(
            tags_time, key=lambda k: k["time"], reverse=True)
        return tags_time

    def get_images(self, page=1, size=15, keyword=''):
        ''' 获取镜像分页列表
        '''
        docker_images = self.__image_list()
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
            tags = self.__get_api(image_api).get('tags', [])
            tags_time = []
            for tag in tags:
                tags_time.append(
                    {"tag": tag, "time": self.__tag_time(image, tag)})
            tags_time = sorted(
                tags_time, key=lambda k: k["time"], reverse=True)
            images_tags.setdefault(image, tags_time)
        return len(docker_images), images_tags

    def search_images(self, key):
        ''' 搜索镜像
        '''
        docker_images = self.__image_list()
        images_tags = {}
        count = 0
        for image in docker_images:
            if key not in image:
                continue
            api = "/v2/" + image + "/tags/list"
            tags = self.__get_api(api).get('tags', [])
            tags_time = []
            for tag in tags:
                tags_time.append(
                    {"tag": tag, "time": self.__tag_time(image, tag)})
            tags_time = sorted(
                tags_time, key=lambda k: k["time"], reverse=True)
            images_tags.setdefault(image, tags_time)
            count += 1
        return count, images_tags
