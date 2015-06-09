#!/usr/bin/env python
# -*- coding:utf8 -*-
# 用户模块

import tornado.web
import tornado.gen
import json
import md5

from index import BaseHandler
from tornado.concurrent import run_on_executor
from concurrent.futures import ThreadPoolExecutor

class UserListHandler(BaseHandler):
    executor = ThreadPoolExecutor(15)
    
    @tornado.web.authenticated
    def get(self):
        self.render("user_list.html",
                    web_title=self.title,
                    user=self.current_user,
                    page="用户列表")

    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):
        data = yield self.GetData()
        self.write(data)
        self.finish()

    @run_on_executor
    def GetData(self):
        data = self.db.query("select user_email,user_name,user_qq,user_phone from user")
        return json.dumps({"data": data,"count": len(data)})


class UserMessageGetHandler(BaseHandler):  
    @tornado.web.authenticated
    def get(self):
        data = self.db.get("select user_email,user_name,user_qq,user_phone from user \
                            where user_email = '{0}' limit 1;".format(self.current_user))
        self.render("user_message.html",
                    web_title=self.title,
                    user=self.current_user,
                    data=data,
                    page="用户信息")

class UserMessagePostHandler(BaseHandler):
    executor = ThreadPoolExecutor(15)
            
    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):
        user_data = json.loads(self.get_argument("user_data"))
        data = yield self.PostData(user_data["name"],
                                  user_data["qq"],
                                  user_data["phone"])
        self.write(data)
        self.finish()

    @run_on_executor
    def PostData(self,name,qq,phone):
        field = {"user_name": name,
                 "user_qq": qq,
                 "user_phone": phone,
                 "user_email": self.current_user}
        data = self.db.execute_rowcount("update user set user_name='{user_name}',\
                                        user_qq='{user_qq}',user_phone='{user_phone}' where \
                                        user_email = '{user_email}' limit 1".format(**field))
        return data and '信息修改成功' or '修改失败'

class UserPasswdHandler(BaseHandler):
    executor = ThreadPoolExecutor(15)
    
    @tornado.web.authenticated
    def get(self):
        self.render("user_passwd.html",
                    web_title=self.title,
                    user=self.current_user,
                    page="密码修改")

    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):
        old_passwd = self.get_argument("old_passwd")
        new_passwd = self.get_argument("new_passwd")
        data = yield self.PostData(old_passwd,new_passwd)
        self.write(data)
        self.finish()

    @run_on_executor
    def PostData(self,old,new):
        data = self.db.get("select user_email,user_passwd from user where user_email = '%s' limit 1"%self.current_user)
        email = data["user_email"].split("@")[0]
        passwd = self.lock.encrypt(email+old)
        if  passwd == data['user_passwd']:
            sql = "update user set user_passwd = '%s' where user_email = '%s' limit 1"
            data = self.db.execute_rowcount(sql%(self.lock.encrypt(email+new),self.current_user))
            return data and '密码修改成功' or '修改中出错,联系管理员查看日志!'
        else:
            return '旧密码不对，请重新输入'
