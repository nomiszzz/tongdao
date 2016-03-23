#!/usr/bin/env python
# -*- coding:utf-8 -*-

import os
import logging

DEPLOY = 'production'

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
APP_PATH = os.path.join(PROJECT_ROOT, 'app')

SETTINGS = {
    'debug': True,
    'template_path': os.path.join(APP_PATH, 'templates'),
    'static_path': os.path.join(APP_PATH, 'static'),
    'cookie_secret': 'you_never_guess',
    'login_url': '/auth/signin',
    'xsrf_cookies': True
}

MYSQLDB = {
    'host': 'host',
    'db': 'db',
    'user': 'user',
    'password': 'password'
}

REDISDB = {
    'host': 'host',
    'port': 6379,
    'db': 7,
    'password': 'password'
}

LOGGER_NAME = 'tongdao'
LOGGER_LEVEL = logging.DEBUG
ORM_LOGGER_LEVEL = logging.WARNING

WEIXIN = {
    'appid': 'appid',
    'secret': 'secret',
    'redirect_uri': 'https://example.com/auth/callback',
    'authorize_api': 'https://open.weixin.qq.com/connect/oauth2/authorize',
    'access_token_api': 'https://api.weixin.qq.com/sns/oauth2/access_token',
    'user_info_api': 'https://api.weixin.qq.com/sns/userinfo'
}

UPLOADS_DIR = {
    'banner_dir': '~/tongdao/app/static/uploads/banner',
    'award_dir': '~/tongdao/app/static/uploads/award',
    'csv_dir': '/Users/ghost/Rsj217/tongdao/app/static/uploads/csv'
}