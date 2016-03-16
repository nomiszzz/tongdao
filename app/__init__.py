#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghost'

import tornado.web
import tornado.ioloop
from app.libs import router
from app.views import *
from settings import config, logger, port

class Application(tornado.web.Application):
    # def ping_db(self):
    #     logger.info('ping db conn {}'.format(id(dbconn)))
    #     dbconn.query("show variables")
    #     logging.warning("ping database...........")

    def __init__(self):
        super(Application, self).__init__(
                **config.SETTINGS
        )
        # logger.info('init the db conn {}'.format(id(dbconn)))
        # tornado.ioloop.PeriodicCallback(self.ping_db, 60 * 1000).start()

    logger.info('Server %s start listening %s' % (config.DEPLOY, port))
