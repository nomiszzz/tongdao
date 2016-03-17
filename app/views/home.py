#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghost'

import tornado.web
from app.helper import BaseTemplateRequestHandler, has_pet_cache, set_pet_cache, BaseApiRequestHandler
from app.libs import router
from app.helper import gen_random_code, get_to_tomorrow
from app.models.home import Pet, Award
from settings import logger, rdb


@router.Route('/home')
class HomeHandler(BaseTemplateRequestHandler):

    # @tornado.web.authenticated
    def get(self, *args, **kwargs):
        uid = self.current_user
        uid = 1
        # 如果尚未领取,重定向领取列表
        if not has_pet_cache(uid) and not Pet.findone(uid=uid):
            return self.redirect('/pets')

        # 设置领养的缓存
        set_pet_cache(uid)
        # 获取领取用户信息
        user_join_pet_info = Pet.get_info(uid)
        if not user_join_pet_info:
            return  self.redirect('/pets')
        user_join_pet_info.update(nickname=user_join_pet_info['nickname'].decode('unicode-escape'))
        self.render('home.html', user_join_pet_info=user_join_pet_info)


@router.Route('/pets')
class PetsHandler(BaseTemplateRequestHandler):
    """
    领养列表
    """
    # @tornado.web.authenticated
    def get(self):
        # 渲染列表页面
        self.render("pets.html")


@router.Route('/pet/(?P<ptype>\w+)')
class PetHandler(BaseTemplateRequestHandler):
    """
    领养接口,领养成功重定向个人页
    """
    # @tornado.web.authenticated
    def get(self, ptype):
        uid = self.current_user
        uid = 1
        # 如果领取了,重定向个人页
        if has_pet_cache(uid) or Pet.findone(uid=uid):
            logger.info('user {} have get pet'.format(uid))
            return self.redirect('/home')

        # 领养
        pet = Pet(type=ptype, uid=uid)
        try:
            row = pet.insert()
            logger.info('insert pet success {}'.format(row))
            set_pet_cache(uid)
        except Exception, e:
            self.set_status(500)
            logger.error('insert pet error {}'.format(e))
            return self.redirect('/pets')
        self.redirect('/home')

@router.Route('/awards')
class AwardsHandler(BaseTemplateRequestHandler):

    # @tornado.web.authenticated
    def get(self, *args, **kwargs):
        awards = Award.findall()
        for ad in awards:
            setattr(ad, 'code', gen_random_code())
        self.render('awards.html', awards=awards)

@router.Route('/api/v1/keep')
class KeepHandler(BaseApiRequestHandler):
    """ 喂养接口,
    :type_ : eat 投食
             wash 洗澡
             game 有戏

             每天仅能进行一次
    """

    # @tornado.web.authenticated
    def get(self):
        uid = self.current_user
        uid = 1
        type_ = self.get_argument('type', None)
        if not type_:
            self.set_status(400)
            result = dict(code=40011, msg=u'缺少type参数')
            return self.jsonify(result)

        keep_info = self.keep_map(type_)

        key = "uid:{}:keep:{}".format(uid, type_)
        times = rdb.incr(key)
        if times == 1:
            rdb.expire(key, get_to_tomorrow())
        else:
            logger.warning('have try times {}'.format(times))
            result = dict(code=40010, msg=u'每天只能{}一次哦!'.format(keep_info['name']))
            return self.jsonify(result)

        try:
            row = Pet.keep(uid=uid, score=keep_info['score'])
            logger.info('keep pet {}'.format(row))
        except Exception, e:
            self.set_status(500)
            logger.error('keep pet error {}'.format(e))
            result = dict(code=40012, msg=u'更新服务器错误')
            return self.jsonify(result)

        self.set_status(201)
        self.jsonify({})

    @staticmethod
    def keep_map(type_):

        maps = {
            'eat': {'name': u'投食', 'score': 2},
            'wash': {'name': u'洗澡', 'score': 3},
            'game': {'name': u'游戏', 'score': 5}
        }
        return maps[type_]






