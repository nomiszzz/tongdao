#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghost'

from app.libs.tornorm import Model, Integer, String, Time


class Banner(Model):
    __table__ = 'banner'

    id = Integer(length=8, primary_key=True, nullable=False, auto_increment=True, updateable=False)
    name = String(length=20, nullable=True)
    image = String(length=100, nullable=True)
    status = Integer(length=1)


class Award(Model):
    __table__ = 'award'

    id = Integer(length=8, primary_key=True, nullable=False, auto_increment=True, updateable=False)
    name = String(length=150, nullable=True)
    provide = String(length=150, nullable=True)
    image = String(length=20, nullable=True)
    score = Integer(length=8, default=0)
    status = Integer(length=8, default=0)


class Winning(Model):
    __table__ = 'award'

    id = Integer(length=8, primary_key=True, nullable=False, auto_increment=True, updateable=False)
    uid = Integer(length=8, nullable=True)
    aid = Integer(length=8, nullable=True)
    code = String(length=6, nullable=True)
    status = Integer(length=8, nullable=True, default=0)

    @classmethod
    def get_all(cls):
        return cls.raw_query(
            "SELECT uw.id, uw.nickname, a.name as award_name, uw.code, uw.status, a.image as award_image FROM (select w.id, w.aid, u.nickname, w.code, w.status from winning w join user u on u.id = w.uid) uw, award a where a.id = uw.aid")
