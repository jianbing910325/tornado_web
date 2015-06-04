#!/usr/bin/env python
# -*- coding:utf8 -*-
# 主模块

import tornado.web
import md5
import json
from models import session
from models.Crypto_string import Locker

class BaseHandler(tornado.web.RequestHandler):
    def __init__(self, *argc, **argkw):
	super(BaseHandler, self).__init__(*argc, **argkw)
	self.session = session.Session(self.application.session_manager, self)

    @property
    def db(self):
        return self.application.db

    @property
    def lock(self):
        return Locker('This is a key123','This is an IV456')

    def initialize(self):
        self.title = "运维管理平台"
	self.index_img = [('static/webimg/w1.gif','登录页','first'),
                          ('static/webimg/w2.gif','主页','two'),
                          ('static/webimg/w3.gif','控制台','three'),
                          ('static/webimg/w4.gif','主机信息页面','four'),
                          ('static/webimg/w5.gif','添加主机页面','five'),
                          ('static/webimg/w6.gif','修改主机页面','six'),
                          ('static/webimg/w7.gif','命令操作页面','seven'),
                          ('static/webimg/w8.gif','上传文件页面','eight'),
                          ('static/webimg/w9.gif','同步文件页面','nine'),
                          ('static/webimg/w10.gif','文章显示页面','ten'),
                          ('static/webimg/w11.gif','文章创建页面','eleven'),
                          ('static/webimg/w12.gif','命令日志页面','twelve'),
                          ('static/webimg/w13.gif','后台监控查询>页面','thirteen'),
                          ('static/webimg/w14.gif','Zabbix接口页面','fourteen'),
                          ('static/webimg/w15.gif','Zabbix接口子页面1','fifteen'),
                          ('static/webimg/w16.gif','Zabbix接口子页面2','sixteen'),
                          ('static/webimg/w17.gif','定时命令页面','seventeen'),
                          ('static/webimg/w18.gif','定时命令添加页面','eighteen'),
                          ('static/webimg/w19.gif','用户列表','nineteen'),
                          ('static/webimg/w10.gif','用户信息修改页面','twenty'),
                          ('static/webimg/w21.gif','用户修改密码','twenty-one')]
        
    def get_current_user(self):
        return self.session.get("user_name")

    def write_error(self,status_code,**kwargs):
        if status_code == 404:
            self.render("http_code.html",
                        code = status_code,
                        error = "没有找到这个页面",
                        faq = "无法找到文件或页面",
                        message = "我们找遍整个网站都没有找到ta!")
        elif status_code == 500:
            self.render("http_code.html",
                        code = status_code,
                        error = "服务器遇到错误，无法完成请求.",
                        message="内部服务器错误.")
        else:
            self.write("Error code: %s"%status_code)

class LoginHandler(BaseHandler):
    def get(self):
        self.render('login.html',web_title="运维平台登陆",error='')

    @tornado.web.asynchronous
    def post(self):
        username = self.get_argument("username")
        password = username.split("@")[0]+self.get_argument("password")
        passwd = self.db.get("select user_passwd from user where user_email = '%s'"%username)
        if passwd is not None:
            if passwd["user_passwd"] == self.lock.encrypt(password):
                self.session["user_name"] = username
                self.session.save()
                self.write('1')
                self.finish()
            else:
                self.write('0')
                self.finish()
        else:
            self.write('0')
            self.finish()

class LogoutHandler(BaseHandler):
    def get(self):
        self.session["user_name"] = None
        self.session.save()
        self.redirect("/login")

class IndexHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
	index = [{"class": "item active","src": j[0],"content": j[1],"alt": j[2]} if i==0 else {"class": "item","src": j[0],"content": j[1],"alt": j[2]} for i,j in enumerate(self.index_img)]	
        self.render("index.html",
                    web_title=self.title,
                    user=self.current_user,
                    index=index)

    
    @tornado.web.authenticated
    def post(self):
	index = [{"alt": j[1],"pid": i,"src": j[0],"thumb": j[0]} for i,j in enumerate(self.index_img)]
	self.write({"title": "页面展示","id": 1,"start": 0,"data": index})

class DashboardHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render("dashboard.html",
                    web_title=self.title,
                    user=self.current_user,
                    page="")

class MonitoringHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        data = self.db.query("select host_ip from history_host group by host_ip")
        self.render("monitoring.html",
                    web_title=self.title,
                    user=self.current_user,
                    ips=data,
                    page="监控页面")
