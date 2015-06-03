#!/usr/bin/env python
# -*- coding:utf8 -*-
# redis接口

import os
os.environ['PYTHON_EGG_CACHE'] = '/tmp'
import redis

class RedisHash(object):
    def __init__(self,name,namespace='hash',**kwargs):
        self.__db = redis.StrictRedis(**kwargs)
        self.__db.pipeline()
        self.__name = "%s:%s"%(namespace,name)

    def qsize(self):
        return self.__db.hlen(self.__name)

    def empty(self):
        return self.qsize() == 0

    def put(self,key,value):
        self.__db.hset(self.__name,key,value)

    def get(self,key):
        return self.__db.hget(self.__name,key)

    def getall(self):
        return self.__db.hgetall(self.__name)

    def vals(self):
        return self.__db.hvals(self.__name)

    def delete(self,key):
        return self.__db.hdel(self.__name,key)

    def trancate(self):
        self.__db.flushdb()
