#!/usr/bin/env python
# -*- coding:utf-8 -*-

import tornado.web
from app.helper import BaseRequestHandler, has_pet_cache
from app.libs import router
from app.models.home import Pet


@router.Route('/')
class IndexHandler(BaseRequestHandler):

    @tornado.web.authenticated
    def get(self, *args, **kwargs):
        """ 活动首页
            判断是否领取了宝贝,尚未领取显示活动页面,否则跳转个人页
        """
        uid = self.current_user

        if has_pet_cache(uid):
            return self.redirect('/home')
        else:
            if Pet.findone(uid=uid):
                return self.redirect('/home')
        self.render("index.html")

@router.Route('/error')
class ErrorHandler(BaseRequestHandler):
    """ 错误信息输出
    """
    def get(self, *args, **kwargs):

        self.render('500.html')
