#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghost'

from app.libs.tornorm import Model, Integer, String


class Pet(Model):

    __table__ = 'pet'

    id = Integer(length=8, primary_key=True, nullable=False)
    uid = Integer(length=8, nullable=True)
    type = Integer(length=1, nullable=True)

    def __repr__(self):
        return '<Pet {}>'.format(self.nickname)

