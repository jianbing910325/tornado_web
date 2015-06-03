#!/usr/bin/env python
# -*- coding:utf8 -*-
# 命令模块

import tornado.web
import tornado.gen
import json
from datetime import datetime
from index import BaseHandler
from tornado.concurrent import run_on_executor
from concurrent.futures import ThreadPoolExecutor

class CommandHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        data = self.db.query("select host_name,host_ip from host;")
        self.render("command.html",
                    web_title=self.title,
                    user=self.current_user,
                    page="命令提示符",
                    action="",
                    data=data)

class CommandACHandler(BaseHandler):
    executor = ThreadPoolExecutor(15)
    
    @tornado.web.authenticated
    def get(self,method):
        if method == 'ips':
            data = self.db.query("select host_name,host_ip from host;")
            self.render("command.html",
                        web_title=self.title,
                        user=self.current_user,
                        page="命令提示符",
                        action="ips",
                        data=data)
            
        elif method == 'group':
            data = self.db.query("select host_group from host_group")
            self.render("command.html",
                        web_title=self.title,
                        user=self.current_user,
                        page="命令提示符",
                        action="group",
                        group=data)

        elif method == 'log':
            thead = ['ID',"用户名","时间","主机名","主机IP","执行命令"]
            data = self.db.query("select a.id,b.user_name,a.date,a.host,a.ip,a.command \
                from command_logs a,user b where a.user_id=b.user_id;")
            if data:
                for i in data:
                    for k,v in i.items():
                        if isinstance(v,type(datetime.now())):
                            i[k] = datetime.strftime(v,"%Y-%m-%d %H:%M:%S")
            self.render("command_log.html",
                        web_title=self.title,
                        user=self.current_user,
                        page="用户命令日志",
                        thead=thead,
                        tbody=data,
                        count=len(data))
        else:
            raise tornado.web.HTTPError(404)
