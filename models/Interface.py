#!/usr/bin/env python
# -*- coding:utf8 -*-

import torndb
import tornado.web
import tornado.gen
import json
import os,sys
import paramiko
import ConfigParser

from datetime import datetime
from views.index import BaseHandler
from RedisHash import RedisHash
from tornado.options import options
from tornado.concurrent import run_on_executor
from concurrent.futures import ThreadPoolExecutor

class CommandInterface(BaseHandler):
    executor = ThreadPoolExecutor(15)

    def initialize(self):
        config = ConfigParser.RawConfigParser()
        config.read('models/db.conf')
        self.__db = torndb.Connection(config.get('db_options','host'),
                                      config.get('db_options','db'),
                                      config.get('db_options','user'),
                                      config.get('db_options','passwd'),
                                      connect_timeout = config.getint('db_options','timeout'),
                                      charset = config.get('db_options','charset'),
                                      time_zone = config.get('db_options','time_zone'))
    @tornado.web.authenticated
    def get(self):
        group = self.get_argument("group")
        data = self.__db.query("select host_ip from host where host_group = '%s'"%group)
        ips = ','.join([i['host_ip'] for i in data])
        self.write(ips)
        
    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):
        ip = self.get_argument('ipaddr')
        comm = self.get_argument('command')
        data = yield self.GetData(ip,comm)
        self.write(data)
        self.finish()

    @run_on_executor
    def GetData(self,ipaddr,command,stdoutMsg="",stderrMsg=""):
        comlist = ['rm',':(){:|:&};:','>/dev/','mv','mkfs.ext',
                   'dd','reboot','halt','init','set','ln','sysctl',
                   'touch','mkdir','vi','exec','eval','export']
        try:
            data = self.__db.get("select host_name,host_passwd from host where \
                            host_ip = '{0}' limit 1;".format(ipaddr))
            passwd = self.lock.decrypt(data["host_passwd"])
        except Exception:
            raise tornado.web.HTTPError(500)
        
        for i in comlist:
            if command.startswith(i):
                return u"消息来自 {0}: \n\n不允许在该主机IP:{1} 中使用该命令!\n".format(data["host_name"],ipaddr)

        user_id = self.__db.get("select user_id from user where user_email='%s' limit 1;"%self.current_user)
        self.__db.execute("insert into command_logs values(null,'%s',now(),'%s','%s','%s');"%(user_id["user_id"],
                                                                                              data["host_name"],
                                                                                              ipaddr,
                                                                                              command))
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect('%s'%ipaddr,22,'root','%s'%passwd,timeout=30)
        except Exception as e:
            return u"消息来自 {0}: \n\n无法连接当前IP: {1},错误信息: {2}\n".format(data["host_name"],ipaddr,e)
        _,stdout,stderr = ssh.exec_command("%s"%command)
        stderrMsg += stderr.read()
        stdoutMsg += stdout.read()
        return u"消息来自 {0}: \n\n{1}\n".format(data["host_name"],stderrMsg+stdoutMsg)
    
class FileInterface(BaseHandler):
    executor = ThreadPoolExecutor(15)

    def initialize(self):
        config = ConfigParser.RawConfigParser()
        config.read('models/db.conf')
        self.__db = torndb.Connection(config.get('db_options','host'),
                                      config.get('db_options','db'),
                                      config.get('db_options','user'),
                                      config.get('db_options','passwd'),
                                      connect_timeout = config.getint('db_options','timeout'),
                                      charset = config.get('db_options','charset'),
                                      time_zone = config.get('db_options','time_zone'))
        
    @tornado.web.authenticated
    def get(self):
        for i in self.get_argument('delete').split(','):
            if os.path.exists(i):
                os.remove(i)
                self.__db.execute("delete from upload_file where new_filename='%s' limit 1;"%os.path.basename(i))
            else:
                data = "没有找到这个文件%s,请查看\n"%i
        try:
            data += "其他文件成功删除"
        except Exception:
            data = "文件全部删除成功"
        self.write(data)
    
    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):
        arg = (self.get_argument('ipaddr'),self.get_argument('file'),self.get_argument('remote'))
        data = yield self.GetData(*arg)
        self.write(data)
        self.finish()
        
    @run_on_executor
    def GetData(self,ipaddr,local_files,remote_dir):
        try:
            data = self.__db.get("select host_name,host_passwd from host where \
                            host_ip = '{0}' limit 1;".format(ipaddr))
            passwd = self.lock.decrypt(data["host_passwd"])
        except Exception:
            raise tornado.web.HTTPError(500)
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect('%s'%ipaddr,22,'root','%s'%passwd,timeout=30)
        except Exception as e:
            return u"消息来自 {0}: \n\n无法连接当前IP: {1},错误信息: {2}\n".format(data["host_name"],ipaddr,e)
        stdin,stdout,stderr = ssh.exec_command("[ -d %s ] && echo 'ok'"%(remote_dir))
        if not stdout.read():
            return u"消息来自 {0}: \n没有这个上传目录{1}\n".format(data["host_name"],remote_dir)
        sftp = ssh.open_sftp()
        files = local_files.split(',')
        try:
            for i in files:
                #remote = os.path.join(remote_dir,i.split('\\')[-1])
                filename = os.path.basename(i)
                old_name = self.__db.get("select old_filename from upload_file where new_filename='%s' limit 1"%filename)
                remote = remote_dir+'/'+old_name["old_filename"]
                sftp.put(i,remote)
                sftp.chmod(remote,0644)
            sftp.close()
        except Exception as e:
            return u"消息来自 {0}: \n文件没有找到，上传失败! 错误消息: {1}\n".format(data["host_name"],e)
        return u"消息来自 {0}: \n所有文件上传成功!\n".format(data["host_name"])
        
class CountInterface(BaseHandler):
    executor = ThreadPoolExecutor(15)

    def initialize(self):
        self.DBDict = {'report': 'reports',
                       'error': 'errors',
                       'log': 'logs',
                       }
        self.Id = {'user':'user_id',
                   'blog': 'blog_id'}
        
        config = ConfigParser.RawConfigParser()
        config.read('models/db.conf')
        self.__db = torndb.Connection(config.get('db_options','host'),
                                      config.get('db_options','db'),
                                      config.get('db_options','user'),
                                      config.get('db_options','passwd'),
                                      connect_timeout = config.getint('db_options','timeout'),
                                      charset = config.get('db_options','charset'),
                                      time_zone = config.get('db_options','time_zone'))
        
    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        getname = self.get_argument('data')
        data = yield self.GetData(getname)
        self.write(data)
        self.finish()

    @run_on_executor
    def GetData(self,getname):
        cid = self.Id.has_key(getname) and self.Id[getname] or "id"
        num = self.__db.get("select count(%s) as count from %s;"%(cid,
                                                                  getname))
        return str(num["count"])

    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):
        getname = self.get_argument('data')
        data = yield self.PostData(getname)
        self.write(data)
        self.finish()

    @run_on_executor
    def PostData(self,getname):
        cid = self.Id.has_key(getname) and self.Id[getname] or "id"
        num = self.__db.get("select count(%s) as count from %s;"%(cid,
                                                                  self.DBDict[getname]))
        data = self.__db.query("select id,message from %s order by id desc limit 5;"%self.DBDict[getname])              
        return json.dumps({"data": data,
                           "count": int(num["count"])})

class Monitoring(BaseHandler):
    executor = ThreadPoolExecutor(15)

    def initialize(self):
        self.redis_options = dict(host=self.application.redis["redis_host"],
                                  port=self.application.redis["redis_port"],
                                  password=self.application.redis["redis_pass"],
                                  db=2)

        config = ConfigParser.RawConfigParser()
        config.read('models/db.conf')
        self.__db = torndb.Connection(config.get('db_options','host'),
                                      config.get('db_options','db'),
                                      config.get('db_options','user'),
                                      config.get('db_options','passwd'),
                                      connect_timeout = config.getint('db_options','timeout'),
                                      charset = config.get('db_options','charset'),
                                      time_zone = config.get('db_options','time_zone'))
    
    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def get(self):
        data = yield self.GetData()
        self.write(data)
        self.finish()

    @run_on_executor
    def GetData(self):
        redis = RedisHash("localhost","host",**self.redis_options)
        return json.dumps(redis.getall())

    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self):
        get_ip = self.get_argument('ipaddr')
        data = yield self.PostData(get_ip)
        self.write(data)
        self.finish()

    @run_on_executor
    def PostData(self,ip):
        if ip == "localhost":
            data = self.__db.query("select * from history;")
        else:
            data = self.__db.query("select * from history_host where host_ip='%s';"%ip)
        if data:    
            for i in data:
                for k,v in i.items():
                    if isinstance(v,type(datetime.now())):
                        i[k] = datetime.strftime(v,"%Y-%m-%d %H:%M:%S")
        return json.dumps(data)
        
