#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghost'


import json
import random
import tornado.web
from app.libs import session
from settings import rdb


class BaseRequestHandler(tornado.web.RequestHandler):
    def initialize(self):
        self.session = session.Session(self.application.session_manager, self)

    def get_current_user(self):
        super(BaseRequestHandler, self).get_current_user()
        uid = self.session.get('uid')
        if not uid:
            return None
        return uid

    def jsonify(self, data):
        self.finish(json.dumps(data))


class BaseTemplateRequestHandler(BaseRequestHandler):
    def get_template_namespace(self):
        namespace = super(BaseTemplateRequestHandler, self).get_template_namespace()
        namespace.update(
                session=self.session
        )
        return namespace


class BaseApiRequestHandler(BaseRequestHandler):
    def check_xsrf_cookie(self):
        return True

    def set_default_headers(self):
        self.set_header('Access-Control-Allow-Origin', '*')
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')
        self.set_header('Access-Control-Max-Age', 1000)
        self.set_header('Access-Control-Allow-Headers', '*')
        self.set_header('Content-type', 'application/json')
        self.set_header('Cache-Control', 'no-store')
        self.set_header('Pragma', 'no-store')


def has_pet_cache(uid):
    """ 缓存是否领养了宝贝
    """
    key = 'uid:{}:getpet'.format(uid)
    if rdb.get(key):
        return True
    return False


def set_pet_cache(uid):
    """ 设置领养了宝贝的缓存
    """
    key = 'uid:{}:getpet'.format(uid)
    rdb.set(key, '1')
    rdb.expire(key, 60*60)


def gen_random_code(length=6):
    chars='0123456789'
    return ''.join([random.choice(chars) for i in range(length)])