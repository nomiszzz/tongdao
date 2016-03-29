#!/usr/bin/env python
# -*- coding:utf-8 -*-

import hashlib
import json
import time

import tornado.gen
import tornado.httpclient
import tornado.web
from app.helper import BaseRequestHandler, BaseApiRequestHandler, gen_password
from app.libs import router
from app.models.auth import User
from settings import config, logger, rdb


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

        # if data.get('errcode') == 45009:
        #     self.redirect('error')

        openid = data['openid']
        sex = data['sex']
        nickname = data['nickname'].encode('unicode-escape')
        avatar = '{}64'.format(data['headimgurl'][:-1])

        user = User.findone(openid=openid)
        if user:
            uid = user['id']
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
            user = User(nickname=nickname, avatar=avatar, openid=openid, sex=sex)
            try:
                row = user.insert()
                uid = row
                logger.info('insert user success {}'.format(row))
            except Exception, e:
                logger.error('insert user error {}'.format(e))
                self.set_status(500)
                self.redirect('/error')
                return

        logger.info('user id {}'.format(row))

        # 存储session
        self.session['uid'] = uid
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


@router.Route('/api/v1/weixin/share')
class ActivityTransformHandler(BaseApiRequestHandler):
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        remote_url = self.get_argument("url")
        appid = config.WEIXIN['appid']
        secret = config.WEIXIN['secret']

        token_key = "wx:api:access_token"
        ticket_key = "wx:api:js_ticket"

        if rdb.exists("%s" % token_key):
            access_token = rdb.get(token_key)
        else:
            http_client = tornado.httpclient.AsyncHTTPClient()
            url = "https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential" \
                  "&appid={}&secret={}".format(appid, secret)

            resp = yield tornado.gen.Task(http_client.fetch, url, method="GET", validate_cert=False)
            try:
                data = json.loads(resp.body)
            except Exception, e:
                logger.error("api.weixin response error: {}".format(e))
                self.set_status(500)
                self.finish()
                return

            access_token = data['access_token']
            rdb.set(token_key, access_token)
            rdb.expire(token_key, data['expires_in'])

        if rdb.exists("%s" % ticket_key):
            js_ticket = rdb.get(ticket_key)
        else:
            http_client = tornado.httpclient.AsyncHTTPClient()
            url = "https://api.weixin.qq.com/cgi-bin/ticket/getticket?access_token={}&type=jsapi".format(access_token)
            resp = yield tornado.gen.Task(http_client.fetch, url, method="GET", validate_cert=False)
            data = json.loads(resp.body)
            js_ticket = data['ticket']
            rdb.set(ticket_key, js_ticket)
            rdb.expire(ticket_key, data['expires_in'])

        noncestr = gen_password()
        timestamp = int(time.time())
        jsapi_ticket = "jsapi_ticket={}&noncestr={}&timestamp={}&url={}".format(
                js_ticket, noncestr, timestamp, remote_url)
        signature = hashlib.sha1(jsapi_ticket).hexdigest()

        logger.info("ticket {}".format(js_ticket))
        logger.info("url: {}".format(remote_url))
        logger.info('noncestr: {}'.format(noncestr))
        logger.info('timestamp: {}'.format(timestamp))
        logger.info('signature: {}'.format(signature))

        result = dict(timestamp=timestamp, nonceStr=noncestr, signature=signature, appId=appid, url=remote_url)
        self.finish(json.dumps(result, ensure_ascii=False))
