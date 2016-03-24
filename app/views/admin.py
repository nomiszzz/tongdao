#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghost'

import os
import csv
import time
from app.models.auth import Admin
from app.models.admin import Banner, Award, Winning
from app.helper import AdminBaseHandler, admin_require, encrypt_password, parse_file_extension
from app.libs import router
from settings import logger, config, rdb


@router.Route('/admin')
class AdminHandler(AdminBaseHandler):
    @admin_require
    def get(self, *args, **kwargs):
        self.render('admin.html')


@router.Route('/admin/login')
class AdminLoginHandler(AdminBaseHandler):
    def get(self):
        self.render('admin-login.html')

    def post(self):
        username = self.get_argument('username', None)
        password = self.get_argument('password', None)
        if not username:
            error, message = True, u"请输入用户名"
        elif not password:
            error, message = True, u"请输入密码"
        else:
            admin = Admin.findone(username=username)
            if not admin:
                error, message = True, u"管理员不存在"
            elif encrypt_password(password) != admin.password:
                error, message = True, u"管理员密码错误"
            else:
                self.session['admin'] = 'admin'
                self.session.save()
                return self.redirect('/admin')
        # 渲染列表页面
        self.render('admin-login.html', error=error, message=message)


@router.Route('/admin/logout')
class AdminLogoutHandler(AdminBaseHandler):
    @admin_require
    def get(self):
        self.session.pop('admin')
        self.session.save()
        error, message = False, u'登出成功'
        self.render('admin-login.html', error=error, message=message)


@router.Route('/admin/banners')
class AdminBannersHandler(AdminBaseHandler):
    @admin_require
    def get(self):
        banners = Banner.findall()
        self.render('admin-banners.html', banners=banners)


@router.Route('/admin/banner/(?P<bid>\d+)/update')
class AdminBannerUpdateHandler(AdminBaseHandler):
    @admin_require
    def get(self, bid):
        banner = Banner.findone(id=bid)
        self.render('admin-banner-update.html', banner=banner)

    @admin_require
    def post(self, bid):
        banner = Banner.findone(id=bid)
        name = self.get_argument('name')
        status = self.get_argument('status')

        if name:
            banner.name = name
        if status:
            banner.status = status

        # 图片上传
        if self.request.files:
            files_body = self.request.files['file']
            file_ = files_body[0]
            # 文件扩展名处理
            file_extension = parse_file_extension(file_)

            # 新建上传目录
            base_dir = config.UPLOADS_DIR['banner_dir']
            if not os.path.exists(base_dir):
                os.makedirs(base_dir)
            logger.info('new dir ---------- {}'.format(base_dir))

            new_file_name = '{}{}'.format(time.time(), file_extension)
            new_file = os.path.join(base_dir, new_file_name)

            # 备份以前上传的文件
            if os.path.isfile(new_file):
                bak_file_name = '{}bak{}'.format(time.time(), file_extension)
                bak_file = os.path.join(base_dir, bak_file_name)
                os.rename(new_file, bak_file)

            # 写入文件
            with open(new_file, 'w') as w:
                w.write(file_['body'])
            new_file_url = '{}{}'.format('/static/uploads/banner/', new_file_name)
            logger.info('new file url {}'.format(new_file_url))
            banner.image = new_file_url
        try:
            row = banner.update()
            logger.info('update banner row {}'.format(row))
        except Exception, e:
            logger.error('update banner error {}'.format(e))
            error, message = True, u'修改失败'
            self.render('admin-banner-update.html', banner=banner, error=error, message=message)
        else:
            self.redirect('/admin/banners')


@router.Route('/admin/banner/add')
class AdminBannerAddHandler(AdminBaseHandler):
    @admin_require
    def get(self):
        self.render('admin-banner-add.html')

    @admin_require
    def post(self):

        name = self.get_argument('name')
        if not name:
            error, message = True, u'请填写banner说明'
            return self.render('admin-banner-add.html', error=error, message=message)
        status = self.get_argument('status')

        # 图片上传
        if self.request.files:
            files_body = self.request.files['file']
            file_ = files_body[0]
            # 文件扩展名处理
            file_extension = parse_file_extension(file_)

            # 新建上传目录
            base_dir = config.UPLOADS_DIR['banner_dir']
            if not os.path.exists(base_dir):
                os.makedirs(base_dir)
            logger.info('new dir ---------- {}'.format(base_dir))

            new_file_name = '{}{}'.format(time.time(), file_extension)
            new_file = os.path.join(base_dir, new_file_name)

            # 备份以前上传的文件
            if os.path.isfile(new_file):
                bak_file_name = '{}bak{}'.format(time.time(), file_extension)
                bak_file = os.path.join(base_dir, bak_file_name)
                os.rename(new_file, bak_file)

            # 写入文件
            with open(new_file, 'w') as w:
                w.write(file_['body'])
            new_file_url = '{}{}'.format('/static/uploads/banner/', new_file_name)
            logger.info('new file url {}'.format(new_file_url))
        else:
            error, message = True, u'请选择照片'
            return self.render('admin-banner-add.html', error=error, message=message)
        banner = Banner(name=name, image=new_file_url, status=status)

        try:
            row = banner.insert()
            logger.info('insert banner row {}'.format(row))
        except Exception, e:
            logger.error('insert banner error {}'.format(e))
            error, message = True, u'添加失败'
            self.render('admin-banner-add.html', error=error, message=message)
        else:
            self.redirect('/admin/banners')


@router.Route('/admin/awards')
class AdminAwardsHandler(AdminBaseHandler):
    @admin_require
    def get(self, *args, **kwargs):
        awards = Award.findall()
        for ad in awards:
            key = 'aid:{}'.format(ad['id'])
            counts = rdb.llen(key)
            setattr(ad, 'counts', counts)
        self.render('admin-awards.html', awards=awards)


@router.Route('/admin/award/(?P<aid>\d+)/update')
class AwardHandler(AdminBaseHandler):
    @admin_require
    def get(self, aid):
        award = Award.findone(id=aid)
        self.render('admin-award-update.html', award=award)

    @admin_require
    def post(self, aid):
        award = Award.findone(id=aid)
        name = self.get_argument('name')
        provide = self.get_argument('provide')
        score = self.get_argument('score')
        status = self.get_argument('status')

        if name:
            award.name = name

        if provide:
            award.provide = provide

        if score:
            award.score = int(score)

        if status:
            award.status = int(status)

        # 图片上传
        if self.request.files:
            files_body = self.request.files['file']
            file_ = files_body[0]
            # 文件扩展名处理
            file_extension = parse_file_extension(file_)

            # 新建上传目录
            base_dir = config.UPLOADS_DIR['award_dir']
            if not os.path.exists(base_dir):
                os.makedirs(base_dir)
            logger.info('new dir ---------- {}'.format(base_dir))

            new_file_name = '{}{}'.format(time.time(), file_extension)
            new_file = os.path.join(base_dir, new_file_name)

            # 备份以前上传的文件
            if os.path.isfile(new_file):
                bak_file_name = '{}bak{}'.format(time.time(), file_extension)
                bak_file = os.path.join(base_dir, bak_file_name)
                os.rename(new_file, bak_file)

            # 写入文件
            with open(new_file, 'w') as w:
                w.write(file_['body'])
            new_file_url = '{}{}'.format('/static/uploads/award/', new_file_name)
            logger.info('new file url {}'.format(new_file_url))
            award.image = new_file_url
        try:
            row = award.update()
            logger.info('update award row {}'.format(row))
        except Exception, e:
            logger.error('update award error {}'.format(e))
            error, message = True, u'修改失败'
            self.render('admin-award-update.html', award=award, error=error, message=message)
        else:
            self.redirect('/admin/awards')


@router.Route('/admin/award/add')
class AdminAwardHandler(AdminBaseHandler):
    @admin_require
    def get(self):
        self.render('admin-award-add.html')

    @admin_require
    def post(self):

        status = self.get_argument('status')
        name = self.get_argument('name')
        if not name:
            error, message = True, u'请填写奖品说明'
            return self.render('admin-award-add.html', error=error, message=message)

        provide = self.get_argument('provide')
        if not provide:
            error, message = True, u'请填提供商'
            return self.render('admin-award-add.html', error=error, message=message)

        score = self.get_argument('score')

        if not score:
            try:
                score = int(score)
            except Exception, e:
                error, message = True, u'兑换点数仅为数字'
            else:
                error, message = True, u'请填兑换点数,仅为数字'
            return self.render('admin-award-add.html', error=error, message=message)

        # 图片上传
        if self.request.files:
            files_body = self.request.files['file']
            file_ = files_body[0]
            # 文件扩展名处理
            file_extension = parse_file_extension(file_)

            # 新建上传目录
            base_dir = config.UPLOADS_DIR['banner_dir']
            if not os.path.exists(base_dir):
                os.makedirs(base_dir)
            logger.info('new dir ---------- {}'.format(base_dir))

            new_file_name = '{}{}'.format(time.time(), file_extension)
            new_file = os.path.join(base_dir, new_file_name)

            # 备份以前上传的文件
            if os.path.isfile(new_file):
                bak_file_name = '{}bak{}'.format(time.time(), file_extension)
                bak_file = os.path.join(base_dir, bak_file_name)
                os.rename(new_file, bak_file)

            # 写入文件
            with open(new_file, 'w') as w:
                w.write(file_['body'])
            new_file_url = '{}{}'.format('/static/uploads/banner/', new_file_name)
            logger.info('new file url {}'.format(new_file_url))
        else:
            error, message = True, u'请选择照片'
            return self.render('admin-award-add.html', error=error, message=message)
        award = Award(name=name, provide=provide, score=score, image=new_file_url, status=int(status))

        try:
            row = award.insert()
            logger.info('insert award row {}'.format(row))
        except Exception, e:
            logger.error('insert award error {}'.format(e))
            error, message = True, u'添加失败'
            self.render('admin-award-add.html', error=error, message=message)
        else:
            self.redirect('/admin/awards')


@router.Route('/admin/winnings')
class AdminWinningsHandler(AdminBaseHandler):
    @admin_require
    def get(self, *args, **kwargs):
        winnings = Winning.get_all()
        for wn in winnings:
            wn['nickname'] = wn['nickname'].decode('unicode-escape')
        self.render('admin-winnings.html', winnings=winnings)


@router.Route('/admin/award/(?P<aid>\d+)/upload')
class AdminUploadHandler(AdminBaseHandler):
    @admin_require
    def get(self, aid):
        self.render('admin-award-upload.html', aid=aid)

    @admin_require
    def post(self, aid):

        # 图片上传
        if self.request.files:
            files_body = self.request.files['file']
            file_ = files_body[0]
            # 文件扩展名处理
            file_extension = parse_file_extension(file_)

            # 新建上传目录
            base_dir = config.UPLOADS_DIR['csv_dir']
            if not os.path.exists(base_dir):
                os.makedirs(base_dir)
            logger.info('new dir ---------- {}'.format(base_dir))

            new_file_name = '{}{}'.format(time.time(), file_extension)
            new_file = os.path.join(base_dir, new_file_name)

            # 备份以前上传的文件
            if os.path.isfile(new_file):
                bak_file_name = '{}bak{}'.format(time.time(), file_extension)
                bak_file = os.path.join(base_dir, bak_file_name)
                os.rename(new_file, bak_file)

            # 写入文件
            with open(new_file, 'w') as w:
                w.write(file_['body'])

            key = 'aid:{}'.format(aid)
            with open(new_file, 'r') as f:
                for line in csv.reader(f):
                    row =  rdb.lpush(key, line[0])
                    logger.info('redis lpush key-- {} resp-- {}'.format(key, row))
        self.redirect('/admin/awards')

@router.Route('/admin/award/(?P<aid>\d+)/codes')
class AdminCodesHandler(AdminBaseHandler):

    @admin_require
    def get(self, aid):
        key = 'aid:{}'.format(aid)
        end = rdb.llen(key)
        codes = rdb.lrange(key, 0, end)
        self.render('admin-award-codes.html', codes=codes)
