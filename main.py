#!/usr/bin/env python
# -*- coding:utf8 -*-
# author: jianbing530221519@163.com
# 网页接入模块

import os
import base64
import logging
import ConfigParser
from uuid import uuid4

import torndb
import tornado.web
import tornado.httpserver
import tornado.options
import tornado.ioloop
from tornado.options import define,options

from models import session
from models.Interface import CommandInterface,FileInterface,CountInterface,Monitoring

from views.index import IndexHandler,DashboardHandler,LoginHandler,LogoutHandler,MonitoringHandler
from views.host import HostHandler,HostACHandler
from views.command import CommandHandler,CommandACHandler
from views.blog import BlogHandler,BlogACHandler
from views.file import UploadHandler,SyncHandler
from views.user import UserListHandler,UserMessageGetHandler,UserMessagePostHandler,UserPasswdHandler
from views.zabbix import ZabbixHandler,ZabbixInterface,ZabbixMethodHandler
from views.command_cron import CommandCronHandler,CommandCronACHandler


define("port",default=8000,help="port of tornado web",type=int)

class Application(tornado.web.Application):
    def __init__(self):
        settings = dict(
            template_path = os.path.join(os.path.dirname(__file__),"templates"),
            static_path = os.path.join(os.path.dirname(__file__),"static"),
            cookie_secret = base64.b64encode(uuid4().bytes+uuid4().bytes),
            session_secret = base64.b64encode(uuid4().bytes+uuid4().bytes),
            xsrf_cookies = True,
            login_url = "/login",
            gzip = True,
            compress_response = True,
            autoreload = True,
            session_timeout = 60*60,
	    ui_modules = {'Index': IndexModule,'Img': ImgModule},
	    store_options = {
		'redis_host': 'localhost',
                'redis_port': 6379,
                'redis_pass': '!a@b#c4d',
	    },
        )
        
        handlers = [
            (r'/',IndexHandler),
            (r'/interface/command',CommandInterface),
            (r'/interface/file',FileInterface),
            (r'/interface/count',CountInterface),
            (r'/interface/monitoring',Monitoring),
            (r'/zabbix',ZabbixHandler),
            (r'/zabbix/(\w+)',ZabbixMethodHandler),
            (r'/zabbix/(\w+)/(\w+)',ZabbixInterface),
            (r'/dashboard',DashboardHandler),
            (r'/host',HostHandler),
            (r'/host/(\w+)',HostACHandler),
            (r'/command',CommandHandler),
            (r'/command/(\w+)',CommandACHandler),
            (r'/blog',BlogHandler),
            (r'/blog/(\w+)',BlogACHandler),
            (r'/upload',UploadHandler),
            (r'/sync',SyncHandler),
            (r'/user',UserMessageGetHandler),
            (r'/user/passwd',UserPasswdHandler),
            (r'/userpost',UserMessagePostHandler),
            (r'/userlist',UserListHandler),
            (r'/monitoring',MonitoringHandler),
            (r'/command_cron',CommandCronHandler),
            (r'/command_cron/(\w+)',CommandCronACHandler),
            (r'/login',LoginHandler),
            (r'/logout',LogoutHandler),
            (r'/(favicon\.ico)',tornado.web.StaticFileHandler,dict(path=settings["static_path"])),        
        ]
        tornado.web.Application.__init__(self,handlers, **settings)
        config = ConfigParser.RawConfigParser()
        config.read('models/db.conf')
        self.db = torndb.Connection(config.get('db_options','host'),
                                    config.get('db_options','db'),
                                    config.get('db_options','user'),
                                    config.get('db_options','passwd'),
                                    connect_timeout = config.getint('db_options','timeout'),
                                    charset = config.get('db_options','charset'),
                                    time_zone = config.get('db_options','time_zone'))
        self.session_manager = session.SessionManager(settings["session_secret"], settings["store_options"], settings["session_timeout"])
        self.redis = settings["store_options"]

class IndexModule(tornado.web.UIModule):
    def render(self,index):
	return self.render_string('index_ui.html',index=index)

class ImgModule(tornado.web.UIModule):
    def render(self,num,index):
	return self.render_string("index_img.html",index=index,num=num)

if __name__ == '__main__':
    logging.debug("debug ......")
    tornado.options.parse_command_line()
    server = tornado.httpserver.HTTPServer(Application())
    server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
