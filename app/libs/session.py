#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghost'

import redis
import hashlib
import uuid
import hmac
import json
import logging


class InvalidSessionException(Exception):
    """ 无效的session异常 """
    pass


class SessionData(dict):
    """ session原始数据结构，包括 `session_id` 和 `hmac_key`，用于数据库存储和验证
    """
    def __init__(self, session_id, hmac_key):
        super(SessionData, self).__init__()
        self.session_id = session_id
        self.hmac_key = hmac_key

    def __getattr__(self, item):
        try:
            return self[item]
        except KeyError:
            raise AttributeError

    def __setattr__(self, key, value):
        self[key] = value


class Session(SessionData):
    """ Session，获取，设置，更新session
    """

    def __init__(self, session_manager, request_handler):
        self.session_manager = session_manager
        self.request_handler = request_handler
        try:
            current_session = session_manager._get(request_handler)
        except InvalidSessionException:
            current_session = session_manager._get()
        for key, data in current_session.iteritems():
            self[key] = data
        super(Session, self).__init__(current_session.session_id, current_session.hmac_key)

    def save(self):
        """ 设置session，将session对象写入数据库
        """
        self.session_manager._set(self.request_handler, self)


class SessionManager(object):
    """ session 管理类，读取，验证，设置，更新
    """

    def __init__(self, secret, redis_conf, session_timeout):
        self.secret = secret
        self.session_timeout = session_timeout

        try:
            self.redis = redis.StrictRedis(**redis_conf)
        except Exception as e:
            logging.error('redis connection {}'.format(e))

    def _fetch(self, session_id):
        """ 读取数据库，获取session数据
        :param session_id:
        :return: 数据库存储的session
        """
        try:
            raw_data = self.redis.get(session_id)
            if raw_data:
                self.redis.setex(session_id, self.session_timeout, raw_data)
                session_data = json.loads(raw_data)
                if isinstance(session_data, dict):
                    return session_data
                else:
                    return {}
            return {}
        except IOError as e:
            return {}

    def _get(self, request_handler=None):
        """ 读取session，返回 session 对象
        :param request_handler:
        :return:
        """

        if not request_handler:
            session_id = None
            hmac_key = None
        else:
            session_id = request_handler.get_secure_cookie('session_id')
            hmac_key = request_handler.get_secure_cookie('verification')

        if not session_id:
            session_exists = False
            session_id = self._generate_id()
            hmac_key = self._generate_hmac_key(session_id)
        else:
            session_exists = True

        check_hmac_key = self._generate_hmac_key(session_id)

        if hmac_key != check_hmac_key:
            raise InvalidSessionException()


        session = SessionData(session_id, hmac_key)
        if session_exists:
            session_data = self._fetch(session_id)
            for key, data in session_data.iteritems():
                session[key] = data
        return session

    def _set(self, request_handler, session):
        request_handler.set_secure_cookie('session_id', session.session_id, httponly=True)
        request_handler.set_secure_cookie('verification', session.hmac_key, httponly=True)
        session_dict = dict(session.items())
        session_dict.pop('request_handler')
        session_dict.pop('session_manager')
        session_data = json.dumps(session_dict)
        self.redis.setex(session.session_id, self.session_timeout, session_data)

    def _generate_id(self):
        return hashlib.sha256(self.secret + str(uuid.uuid4())).hexdigest()

    def _generate_hmac_key(self, session_id):
        return hmac.new(session_id, self.secret, hashlib.sha256).hexdigest()
