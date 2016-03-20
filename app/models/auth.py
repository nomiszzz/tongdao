#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghost'

from app.libs.tornorm import Model, Integer, String, Time


class User(Model):

    __table__ = 'user'

    id = Integer(length=8, primary_key=True, nullable=False, auto_increment=True, updateable=False)
    openid = String(length=60, nullable=True)
    nickname = String(length=20, nullable=True)
    avatar = String(length=150, nullable=True)
    created_at = Time(length=20)

    def __repr__(self):
        return '<User {}>'.format(self.nickname)


class Admin(Model):
    __table__ = 'admin'

    id = Integer(length=8, primary_key=True, nullable=False, auto_increment=True, updateable=False)
    username = String(length=60, nullable=True)
    password = String(length=20, nullable=True)
