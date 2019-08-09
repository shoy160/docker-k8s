# coding:utf-8
import math
import tornado.web
from services.app import BaseHandler, app
from helper.k8s import get_deploy_image
from helper.utils import get_version, set_version
from tornado.options import options


@app.route('/')
class IndexHandler(BaseHandler):
    @tornado.web.authenticated
    async def get(self):
        page = int(self.get_argument("page", 1))
        size = int(self.get_argument('size', options.page_size))
        key = self.get_argument("key", '')
        total, image_list = await self.registry_api.get_images(page, size, key)
        pages = int(math.ceil(float(total) / size))
        self.render('index.html', registry=self.registry,
                    total=total, pages=pages, currentPage=page, size=size, key=key, list=image_list, user=self.current_user, delete=options.enable_delete)


@app.route('/login')
class LoginViewHandler(BaseHandler):
    def get(self):
        self.render('login.html')


@app.route('/logout')
class LogoutViewHandler(BaseHandler):
    def get(self):
        self.clear_cookie('__registry_u')
        self.redirect('/login')


@app.route('/image/(.*)')
class ImageViewHandler(BaseHandler):
    @tornado.web.authenticated
    async def get(self, *args):
        image = args[0]
        # page = int(self.get_argument("page", 1))
        # size = int(self.get_argument('size', options.page_size))
        total, tag_list = await self.registry_api.get_images_tags(image)
        current_tag = None
        version = None
        if options.enable_k8s:
            arr = image.split('/')
            deploy = arr[0] if len(arr) == 1 else arr[1]
            version = get_version(deploy)
            k8s_image = get_deploy_image(deploy, options.namespace)
            if k8s_image != None:
                c_image = "{0}/{1}".format(self.registry, image)
                current_tag = k8s_image.replace(c_image, '')
                if current_tag:
                    current_tag = current_tag[1:]
                else:
                    current_tag = 'latest'
                if version == None:
                    set_version(deploy, image, current_tag)
                    version = get_version(deploy)
        if current_tag != None:
            for tag in tag_list:
                is_current = tag['name'] == current_tag
                tag['is_current'] = is_current
                if is_current and 'time' in version:
                    tag['publish_time'] = version['time']
                else:
                    tag['publish_time'] = ''
        self.render('tags.html', image=image, total=total,
                    list=tag_list, user=self.current_user, k8s=version, delete=options.enable_delete)


@app.route('/tag/(.*)/(.*)')
class TagViewHandler(BaseHandler):
    @tornado.web.authenticated
    async def get(self, *args):
        image = args[0]
        tag = args[1]
        result = await self.registry_api.get_image_history(image, tag)
        self.render('history.html', user=self.current_user,
                    image=image, tag=tag, count=result['count'], size=result['size'], list=result['history'])
