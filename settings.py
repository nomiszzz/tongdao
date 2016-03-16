#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghost'

import logging
import tornado.util
from tornado.options import define, options

define('env', default='dev')
options.parse_command_line()

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


logger = create_log()
logger.info('logger db conn {}')
