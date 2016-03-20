#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghost'

import tornado.web
from app.helper import BaseRequestHandler, admin_require
from app.libs import router


@router.Route('/admin')
class AdminHandler(BaseRequestHandler):
    @admin_require
    def get(self, *args, **kwargs):
        self.render('admin.html')


@router.Route('/admin/login')
class AdminLoginHandler(BaseRequestHandler):

    def get(self):
        # 渲染列表页面
        self.render('admin-login.html')

    def post(self):
        # 渲染列表页面
        self.finish('login')


@router.Route('/admin/logout')
class AdminLogoutHandler(BaseRequestHandler):
    @admin_require
    def get(self, ptype):
        self.finish('logout')
