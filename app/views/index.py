#!/usr/bin/env python
# -*- coding:utf-8 -*-

from app.helper import BaseRequestHandler
from app.libs import router


@router.Route('/')
class IndexHandler(BaseRequestHandler):
    def get(self, *args, **kwargs):
        self.render("index.html", title="index")


@router.Route('/es6')
class ES6Handler(BaseRequestHandler):
    def get(self, *args, **kwargs):
        self.render('es6.html', title="es6")


@router.Route('/react')
class ReactHandler(BaseRequestHandler):
    def get(self, *args, **kwargs):
        self.render('react-demo.html', title="react")


@router.Route('/about', name='about')
class AboutHandler(BaseRequestHandler):
    def get(self, *args, **kwargs):
        self.render('about.html')
