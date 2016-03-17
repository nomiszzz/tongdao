#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghost'

from app.libs.tornorm import Model, Integer, String, Time


class User(Model):

    __table__ = 'user'

    id = Integer(length=8, primary_key=True, nullable=False)
    openid = String(length=60, nullable=True)
    nickname = String(length=20, nullable=True)
    avatar = String(length=150, nullable=True)
    created_at = Time(length=20)

    def __repr__(self):
        return '<User {}>'.format(self.nickname)

