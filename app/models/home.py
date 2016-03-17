#!/usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = 'ghost'

from app.libs.tornorm import Model, Integer, Time, String


class Pet(Model):
    __table__ = 'pet'

    id = Integer(length=8, primary_key=True, nullable=False)
    uid = Integer(length=8, nullable=True)
    type = Integer(length=1, nullable=True)
    score = Integer(length=8, default=0)
    created_at = Time(length=20)

    def __repr__(self):
        return '<Pet {}>'.format(self.type)

    @classmethod
    def get_info(cls, uid):
        return cls.raw_get("SELECT u.id, u.openid, u.nickname, u.avatar,u.sex, p.type, p.score "
                           "FROM user u JOIN pet p ON u.id=p.uid "
                           "WHERE u.id=%s", uid)

    @classmethod
    def keep(cls, uid, score):
        return cls.raw_update("UPDATE pet SET score=score + %s WHERE uid=%s", score, uid)
        # if score == 2:
        #     return cls.raw_update("UPDATE pet SET score=score + 2 WHERE uid=%s", uid)
        # elif score == 3:
        #     return cls.raw_update("UPDATE pet SET score=score + 3 WHERE uid=%s", uid)
        # else:
        #     return cls.raw_update("UPDATE pet SET score=score + 5 WHERE uid=%s", uid)

class Award(Model):
    __table__ = 'award'

    id = Integer(length=8, primary_key=True, nullable=False)
    name = String(length=150, nullable=True)
    provide = String(length=150, nullable=True)
    image = String(length=20, nullable=True)
    score = Integer(length=8, default=0)
