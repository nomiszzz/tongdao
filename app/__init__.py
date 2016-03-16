#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghost'

import tornado.web
import tornado.ioloop
from app.libs import router
from app.views import *
from settings import config, logger, port, db, session_manager

class Application(tornado.web.Application):
    def ping_db(self):
        logger.info('ping db conn {}'.format(id(db)))
        db.query("show variables")
        logger.warning("ping database...........")

    def __init__(self):
        super(Application, self).__init__(
                **config.SETTINGS
        )
        logger.info('init the db conn {}'.format(id(db)))
        tornado.ioloop.PeriodicCallback(self.ping_db, 60 * 1000).start()

        self.session_manager = session_manager


    logger.info('Server %s start listening %s' % (config.DEPLOY, port))
