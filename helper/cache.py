# coding:utf-8

cache_dict = {}


class CacheHelper():
    ''' 缓存辅助 '''

    def __init__(self, region='system'):
        self.__region = region

    def __get_key(self, key):
        return "%s:%s" % (self.__region, key)

    def has(self, key):
        cache_key = self.__get_key(key)
        return cache_key in cache_dict

    def set(self, key, value):
        ''' 设置缓存
        :param     key:string  缓存键
        :param     value:Object    缓存值,为None时删除
        '''
        cache_key = self.__get_key(key)
        if value is None:
            del cache_dict[cache_key]
        else:
            cache_dict[cache_key] = value

    def get(self, key):
        ''' 获取缓存值
        :param      key:string  缓存键
        '''
        cache_key = self.__get_key(key)
        if cache_key in cache_dict:
            return cache_dict[cache_key]
        return None

    def remove(self, key):
        ''' 删除缓存 '''
        cache_key = self.__get_key(key)
        if cache_key in cache_dict:
            del cache_dict[cache_key]

    def clear(self):
        ''' 清空缓存 '''
        prefix = "%s:" % self.__region
        for key in cache_dict:
            if key.startswith(prefix):
                del cache_dict[key]
