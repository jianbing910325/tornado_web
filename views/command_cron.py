#!/usr/bin/env python
# -*- coding:utf8 -*-
# 定时命令模块

import tornado.web
import tornado.gen
import json
import redis
import os,time
import torndb
import subprocess
import pickle

from datetime import datetime
from tornado.options import options
from index import BaseHandler
from tornado.concurrent import run_on_executor
from concurrent.futures import ThreadPoolExecutor

class CommandCronHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        thead = ['ID','任务名称','执行时间','主机名','主机IP','执行命令','数据返回','返回状态']
        data = self.db.query("select * from task_command")
        self.render("command_cron.html",
                    web_title=self.title,
                    user=self.current_user,
                    thead=thead,
                    tbody=data,
                    page="定时命令结果查询")

class CommandCronACHandler(BaseHandler):
    @property
    def db_redis(self):
        return redis.StrictRedis(host=self.application.redis['redis_host'],
                                 port=self.application.redis['redis_port'],
                                 password=self.application.redis['redis_pass'],
                                 db=6)
        
    @tornado.web.authenticated
    def get(self,method):
        if method == 'add':
            self.render("command_cron_add.html",
                        web_title=self.title,
                        user=self.current_user,
                        page="添加定时任务")

	elif method == 'c_add':
            task_name = self.get_argument("task_name")
            task_date = self.get_argument("task_date")
            task_command = self.get_argument("task_command")
            ips = self.get_argument('ipaddr')
            data = []
            for i in ips.split(","):
                dbd=self.db.get("select host_name,host_code,host_ip from host \
                                where host_ip='{0}' limit 1;".format(i))
	        if dbd:
                    data.append(dbd)
            self.render("command_cron_host.html",
                        name=task_name,
                        date=task_date,
                        command=task_command,
                        tbody=data)

        elif method == 'status':
            thead = ['任务ID','执行时间','执行函数','操作']
            data = []
            for i in self.db_redis.hvals("command.jobs"):
                d = pickle.loads(i)
                for k,v in d.items():
                    if isinstance(v,type(datetime.now())):
                        d[k] = datetime.strftime(v,'%Y-%m-%d %H:%M:%S')
		    else:
			d[k] = str(v)
                data.append(d)
            self.render("command_cron_status.html",
                        web_title=self.title,
                        user=self.current_user,
                        thead=thead,
			tbody=data,
			count=len(data),
                        page="定时任务查询")

        else:
            raise tornado.web.HTTPError(404)

    @tornado.web.authenticated
    @tornado.web.asynchronous
    def post(self,method):
        if method == 'add':
            data = self.get_argument('task_data')
	    db_data = json.loads(data)
	    check = self.db.query("select * from task_command where task_name = '%s' limit 1;"%db_data["task_name"])
	    if check:
		self.write('当前任务名称已经存在,请重新取名')
		self.finish()
	    else:
	        mylist = []
	        for i in range(len(db['host_ip'])):
	    	    mylist.append("(null,'%s','%s','%s','%s','%s','',1)"%(db_data["task_name"],
                                                                          db_data["task_date"],
                                                                          db_data["host_name"][i],
                                                                          db_data["host_ip"][i],
                                                                          db_data["command"]))
	        self.db.execute("insert into task_command values{0};".format(','.join(mylist)))
	        pid = subprocess.Popen(["/usr/bin/nohup","/usr/bin/python2.7","models/command_script.py",data,'&']).pid
	        self.db.execute("insert into task_pid values(null,'command_script.py','%s','%s','%s');"%(db_data["task_date"],data,pid))
	        time.sleep(2)
                self.write('已经加入任务当中，可点击查询按钮查看任务状态 任务id: %s'%pid)
                self.finish()

        elif method == 'del':
            task_id = self.get_argument("task_id")
            self.db_redis.hdel("command.jobs",task_id)
            self.db_redis.zrem("command.run_times",task_id)
            self.write('%s 从定时任务中去除'%task_id)
            self.finish()
        else:
           raise tornado.web.HTTPError(404) 
