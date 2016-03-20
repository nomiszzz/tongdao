#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghost'

from app.models.auth import Admin
from app.models.admin import Banner, Award
from app.helper import AdminBaseHandler, admin_require, encrypt_password
from app.libs import router


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

@router.Route('/admin/banner')
class AdminBannerHandler(AdminBaseHandler):

    @admin_require
    def get(self):
        banners = Banner.findall()
        self.render('admin-banners.html', banners=banners)