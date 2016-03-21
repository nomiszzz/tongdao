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


@router.Route('/emoji')
class EmojiHandle(BaseRequestHandler):

    def get(self, *args, **kwargs):

        from settings import  db


        s = u'中国人\U0001f604'.encode('unicode-escape')
        print s
        db.execute("update user set nickname=%s WHERE id=2", s)

        user = db.get("SELECT * FROM user where id=2")
        r =  user['nickname'].decode('unicode-escape')

        self.write(r)
