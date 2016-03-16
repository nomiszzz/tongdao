#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghost'


from app.helper import BaseTemplateRequestHandler
from app.libs import router
from app.models.home import Pet
from settings import logger


@router.Route('/home')
class HomeHandler(BaseTemplateRequestHandler):

    def get(self, *args, **kwargs):
        uid = self.session['uid']
        pet = Pet.findone(uid=uid)
        if not pet:
            return self.redirect('/pets')





@router.Route('/pets')
class BabiesHandler(BaseTemplateRequestHandler):
    """
    领养列表
    """

    def get(self, *args, **kwargs):

        # 如果领养了,重定向home页面
        uid = self.session['uid']
        if Pet.findone(uid=uid):
            return self.redirect('/home')
        # 渲染列表页面
        self.render("pets.html")


@router.Route('/getpet/?P<ptype>.*')
class BabiesHandler(BaseTemplateRequestHandler):
    """
    领养接口,领养成功重定向个人页
    """
    def get(self, ptype):

        # 如果领养了,重定向home页面
        uid = self.session['uid']
        if Pet.findone(uid=uid):
            return self.redirect('/')

        # 领养
        pet = Pet(type=int(ptype), uid=uid)
        try:
            row = pet.insert()
            logger.info('insert pet success {}'.format(row))
        except Exception, e:
            self.set_status(500)
            logger.error('insert pet error {}'.format(e))
            return self.redirect('/pets')
        self.redirect('/home')

