#!/usr/bin/env python
# -*- coding:utf-8 -*-

import json
import tornado.web
import tornado.gen
import tornado.httpclient
from app.helper import BaseRequestHandler
from app.libs import router
from app.models.auth import User
from settings import config, logger


@router.Route('/auth/signin')
class SigninHandler(BaseRequestHandler):
    """微信授权"""

    def get(self, *args, **kwargs):

        appid = config.WEIXIN['appid']
        authorize_api = config.WEIXIN['authorize_api']
        redirect_uri = config.WEIXIN['redirect_uri']

        authorize_url = (
            "{authorize_api}?appid={appid}&redirect_uri={redirect_uri}&response_type=code&scope=snsapi_login".format(
                authorize_api=authorize_api,
                appid=appid,
                redirect_uri=redirect_uri))
        logger.info(u'weixin authorize url {}'.format(authorize_url))
        return self.redirect(authorize_url)

@router.Route('/auth/callback')
class CallbackHandler(BaseRequestHandler):

    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self, *args, **kwargs):
        # 获取微信返回的授权 code
        code = self.get_argument('code')
        # code 换取 access_token
        appid = config.WEIXIN['appid']
        secret = config.WEIXIN['secret']
        access_token_api = config.WEIXIN['access_token_api']
        access_token_url = '{access_token_api}?appid={appid}&secret={secret}&code={code}&grant_type=authorization_code'.format(
            access_token_api=access_token_api, appid=appid, secret=secret, code=code)

        http_client = tornado.httpclient.AsyncHTTPClient()
        resp = yield tornado.gen.Task(http_client.fetch, access_token_url, method="GET", validate_cert=False)
        logger.info(u'access_token response {}'.format(resp))
        status, data = self._handler_resp(resp.body)
        if not status:
            # 微信授权失败
            self.redirect('/error')
            return

        user_info_api = config.WEIXIN['user_info_api']
        user_info_url = '{user_info_api}?access_token={access_token}&openid={openid}&lang=zh_CN'.format(
            user_info_api=user_info_api, access_token=data['access_token'], openid=data['openid'])

        resp = yield tornado.gen.Task(http_client.fetch, user_info_url, method="GET", validate_cert=False)
        logger.info(u'user info response {}'.format(resp))
        status, data = self._handler_resp(resp.body)
        if not status:
            self.redirect('/error')
            return

        openid = data['openid']
        nickname = data['nickname'].encode('unicode-escape')
        avatar = '{}64'.format(data['headimgurl'][:-1])

        user = User.findone(openid=openid)
        if user:
            # 更新旧用户
            user.nickname = nickname
            user.avatar = avatar
            try:
                row = user.update()
            except Exception, e:
                logger.error('update user error {}'.format(e))
                self.set_status(500)
                self.redirect('/error')
                return
        else:
            # 写入新用户
            user = User(nickname=nickname, avatar=avatar, openid=openid)
            try:
                row = user.insert()
                logger.info('insert user success {}'.format(row))
            except Exception, e:
                logger.error('insert user error {}'.format(e))
                self.set_status(500)
                self.redirect('/error')
                return

        # 存储session
        self.session['uid'] = row
        self.session['openid'] = openid
        self.session.save()

        self.redirect('/')

    def _handler_resp(self, body):
        try:
            data = json.loads(body)
        except Exception, e:
            logger.error('weixin response error {}'.format(e))
            return False, None

        if data.has_key('errcode'):
            return False, None
        else:
            return True, data