#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghost'

import logging
import redis
import tornado.util
from tornado.options import define, options
from app.libs.session import SessionManager
from app.libs.torndb import Connection


define('env', default='dev')
define('port', default=7999)
options.parse_command_line()

port = options.port

if options.env == 'dev':
    config = tornado.util.import_object('config.dev')
elif options.env == 'pro':
    config = tornado.util.import_object('config.pro')
elif options.env == 'test':
    config = tornado.util.import_object('config.test')


def create_log():
    log = logging.getLogger(config.LOGGER_NAME)
    log.setLevel(config.LOGGER_LEVEL)
    return log

def create_session_manager():
    redis_conf = {
        'host': config.REDISDB['host'],
        'port': config.REDISDB['port'],
        'password': config.REDISDB['password'],
        'db': config.REDISDB['db']
    }
    return SessionManager("session_secret", redis_conf, 12 * 30 * 24 * 60 * 60)

def create_redis():
    """ 创建 redis 连接 """
    connection_pool = redis.ConnectionPool(
        host=config.REDISDB['host'],
        port=config.REDISDB['port'],
        db=config.REDISDB['db'],
        password=config.REDISDB['password']
    )

    return redis.Redis(connection_pool=connection_pool)

def create_mysqldb():
    """ 创建 mysql 连接 """
    mdb = Connection(
        host=config.MYSQLDB['host'],
        database=config.MYSQLDB['db'],
        user=config.MYSQLDB['user'],
        password=config.MYSQLDB['password'],
    )
    return mdb



logger = create_log()
session_manager = create_session_manager()

db = create_mysqldb()
logger.info('DB conn {}'.format(id(db)))

rdb = create_redis()
logger.info('Redis DB conn {}'.format(id(rdb)))