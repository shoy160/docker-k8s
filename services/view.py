# coding:utf-8
import math
import tornado.web
from services.app import BaseHandler, app
from helper.k8s import get_deploy_image
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
        tag_list = await self.registry_api.get_images_tags(image)
        current_tag = None
        if options.enable_k8s:
            arr = image.split('/')
            deploy = arr[0] if len(arr)==1 else arr[1]
            k8s_image = get_deploy_image(deploy, options.namespace)
            if k8s_image != None:
                c_image = "{0}/{1}".format(self.registry, image)
                current_tag = k8s_image.replace(c_image, '')
                if current_tag:
                    current_tag = current_tag[1:]
                else:
                    current_tag = 'latest'
        if current_tag != None:
            for tag in tag_list:
                tag['is_current'] = tag['name'] == current_tag
        self.render('tags.html', image=image,
                    list=tag_list, user=self.current_user, k8s=current_tag, delete=options.enable_delete)
