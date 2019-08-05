# coding:utf-8
import os
from services.app import BaseHandler, app
from helper.utils import call_command
from helper.image import RegistryCleaner, RegistryCleanerError
import tornado.web
from tornado.options import options


@app.route('/api/image')
class ImageHandler(BaseHandler):
    @tornado.web.authenticated
    async def get(self):
        ''' 镜像列表
        :param  page:int    
        :param  size:int
        :param  key:str
        '''
        page = int(self.get_argument("page", 1))
        size = int(self.get_argument('size', options.page_size))
        key = self.get_argument("key", '')
        total, image_list = await self.registry_api.get_images(page, size, key)
        self.json_success({
            'total': total,
            'images': image_list
        })


@app.route('/api/image/(.*)')
class ImageTagsHandler(BaseHandler):
    @tornado.web.authenticated
    async def get(self, *args):
        ''' 镜像标签列表
        '''
        image = args[0]
        if image is None or image == '':
            self.json_error('缺少镜像名称参数')
            return
        tag_list = await self.registry_api.get_images_tags(image)
        self.json_success(tag_list)

    # 依赖delete_docker_registry_image
    @tornado.web.authenticated
    def delete(self, *args):
        '''删除镜像
        :param  tag:str     标签(为空，删除整个镜像)
        '''
        if not options.enable_delete:
            self.json_error('delete action is disabled')
            return
        image = args[0]
        tag = self.get_argument("tag", None)
        if image == '':
            self.json_error('镜像名称不能为空')
            return
        # self.json_success({
        #     'image': image,
        #     'tag': tag
        # })        
        if 'REGISTRY_DATA_DIR' in os.environ:
            registry_data_dir = os.environ['REGISTRY_DATA_DIR']
        else:
            registry_data_dir = "/opt/registry_data/docker/registry/v2"
        try:
            cleaner = RegistryCleaner(registry_data_dir)
            if tag:
                tag_count = cleaner.get_tag_count(image)
                if tag_count == 1:
                    cleaner.delete_entire_repository(image)
                else:
                    cleaner.delete_repository_tag(image, tag)
            else:
                cleaner.delete_entire_repository(image)
            self.json_success()
        except RegistryCleanerError as error:
            self.logger.info(error)
            self.json_error('删除镜像失败')

        # execute
        # if tag is not None:
        #     image += ':'+tag
        # command = "delete_docker_registry_image --image {0};docker restart registry-srv".format(
        #     image)
        # self.logger.info(command)
        # status, msg = call_command(command)
        # if status:
        #     self.json_success(msg)
        # else:
        #     self.json_error('删除镜像失败')
