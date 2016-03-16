#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghost'

import json
import tornado.web


class BaseRequestHandler(tornado.web.RequestHandler):
    def jsonify(self, data):
        self.finish(json.dumps(data))


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
