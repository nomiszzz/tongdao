#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghost'


from app.helper import BaseRequestHandler
from app.libs import router

@router.Route('/babies')
class BabiesHandler(BaseRequestHandler):
    def get(self, *args, **kwargs):
        self.render("babies.html")