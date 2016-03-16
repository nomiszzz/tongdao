#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghost'




from app.helper import BaseRequestHandler
from app.libs import router

@router.Route('/login')
class LoginHandler(BaseRequestHandler):
    def get(self, *args, **kwargs):
        self.session['uid'] = 1
        self.session['nickname'] = u'人世间'
        self.session['openid'] = 'openid'
        self.session.save()
        self.finish('login success')


@router.Route('/logout')
class LogoutHandler(BaseRequestHandler):

    def get(self, *args, **kwargs):
        self.session.pop('uid')
        self.session.pop('nickname')
        self.session.pop('openid')
        self.session.save()
        self.finish('logout success')