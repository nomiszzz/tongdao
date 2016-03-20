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

import tornado.web
import tornado.gen
import tornado.auth

class FacebookGraphLoginHandler(tornado.web.RequestHandler,
                                tornado.auth.FacebookGraphMixin):
  @tornado.gen.coroutine
  def get(self):
      if self.get_argument("code", False):
          user = yield self.get_authenticated_user(
              redirect_uri='/auth/facebookgraph/',
              client_id=self.settings["facebook_api_key"],
              client_secret=self.settings["facebook_secret"],
              code=self.get_argument("code"))
          # Save the user with e.g. set_secure_cookie
      else:
          yield self.authorize_redirect(
              redirect_uri='/auth/facebookgraph/',
              client_id=self.settings["facebook_api_key"],
              extra_params={"scope": "read_stream,offline_access"})

class MainHandler(tornado.web.RequestHandler,
                  tornado.auth.FacebookGraphMixin):
    @tornado.web.authenticated
    @tornado.gen.coroutine
    def get(self):
        new_entry = yield self.facebook_request(
            "/me/feed",
            post_args={"message": "I am posting from my Tornado application!"},
            access_token=self.current_user["access_token"])

        if not new_entry:
            # Call failed; perhaps missing permission?
            yield self.authorize_redirect()
            return
        self.finish("Posted a message!")