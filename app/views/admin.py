#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghost'

import os
import time
from app.models.auth import Admin
from app.models.admin import Banner, Award
from app.helper import AdminBaseHandler, admin_require, encrypt_password,parse_file_extension
from app.libs import router
from settings import logger,config


@router.Route('/admin')
class AdminHandler(AdminBaseHandler):
    @admin_require
    def get(self, *args, **kwargs):
        self.render('admin.html')


@router.Route('/admin/login')
class AdminLoginHandler(AdminBaseHandler):

    def get(self):
        self.render('admin-login.html')

    def post(self):
        username = self.get_argument('username', None)
        password = self.get_argument('password', None)
        if not username:
            error, message=True, u"请输入用户名"
        elif not password:
            error, message=True, u"请输入密码"
        else:
            admin = Admin.findone(username=username)
            if not admin:
                error, message=True, u"管理员不存在"
            elif encrypt_password(password) != admin.password:
                error, message=True, u"管理员密码错误"
            else:
                self.session['admin'] = 'admin'
                self.session.save()
                return self.redirect('/admin')
        # 渲染列表页面
        self.render('admin-login.html', error=error, message=message)


@router.Route('/admin/logout')
class AdminLogoutHandler(AdminBaseHandler):
    @admin_require
    def get(self):
        self.session.pop('admin')
        self.session.save()
        error, message = False, u'登出成功'
        self.render('admin-login.html', error=error, message=message)

@router.Route('/admin/banners')
class AdminBannersHandler(AdminBaseHandler):

    @admin_require
    def get(self):
        banners = Banner.findall()
        self.render('admin-banners.html', banners=banners)

@router.Route('/admin/banner/(?P<bid>\d+)')
class AdminBannerHandler(AdminBaseHandler):

    @admin_require
    def get(self, bid):
        banner = Banner.findone(id=bid)
        self.render('admin-banner.html', banner=banner)

    @admin_require
    def post(self, bid):
        banner = Banner.findone(id=bid)
        name =  self.get_argument('name')
        status = self.get_argument('status')

        if name:
            banner.name = name
        if status:
            banner.status = status

        # 图片上传
        if self.request.files:
            files_body = self.request.files['file']
            file_ = files_body[0]
            # 文件扩展名处理
            file_extension = parse_file_extension(file_)

            # 新建上传目录
            base_dir = config.UPLOADS_DIR['banner_dir']
            if not os.path.exists(base_dir):
                os.makedirs(base_dir)
            logger.info('new dir ---------- {}'.format(base_dir))

            new_file_name = '{}{}'.format(time.time(), file_extension)
            new_file = os.path.join(base_dir, new_file_name)

            # 备份以前上传的文件
            if os.path.isfile(new_file):
                bak_file_name = '{}bak{}'.format(time.time(), file_extension)
                bak_file = os.path.join(base_dir, bak_file_name)
                os.rename(new_file, bak_file)

            # 写入文件
            with open(new_file, 'w') as w:
                w.write(file_['body'])
            new_file_url = '{}{}'.format('/static/uploads/banner/', new_file_name)
            logger.info('new file url {}'.format(new_file_url))
            banner.image = new_file_url
        try:
            row = banner.update()
            logger.info('update banner row {}'.format(row))
        except Exception, e:
            logger.error('update banner error {}'.format(e))
            error, message = True, u'修改失败'
            self.render('admin-banner.html', banner=banner, error=error, message=message)
        else:
            self.redirect('/admin/banners')


