#!/usr/bin/env python
# -*- coding:utf8 -*-
#定时获取系统相关的一些数据,作为监控

import sys
import paramiko
import json
import apscheduler
from RedisHash import RedisHash
from subprocess import Popen,PIPE
from tornado.ioloop import IOLoop
import apscheduler.events
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.schedulers.tornado import TornadoScheduler
from apscheduler.executors.pool import ThreadPoolExecutor
import torndb

class Host_Get(object):
    def __init__(self, namespace,db):
        self.__name = namespace
        self.redis_options = dict(host="127.0.0.1",
                         port=6379,
                         password="!a@b#c4d",
                         db=2)

        self.__mysql_db = db

        self.commands = {"cpu_use": "/usr/bin/top -bcn 1 | awk -F '[%| ]+' '/[Cc]pu/{a+=1;for(i=1;i<NF;i++)if($i ~ /us/) b+=$(i-1)}END{print b/a}'",
                    "cpu_iowait": "/usr/bin/top -bcn 1 | awk -F '[%| ]+' '/[Cc]pu/{a+=1;for(i=1;i<NF;i++)if($i ~ /wa/) b+=$(i-1)}END{print b/a}'",
                    "mem_use": "free -m | awk 'NR==2{a=$2}NR==3{b=$3}END{printf(\"%d\",b/a*100)}'",
                    "swap_use": "free -m | awk '/dwap/{a=$3/$2*100;p=1}END{if(p=1){printf(\"%d\",a)}else{print \"no data\"}}'",
                    "root_use": "df -h | awk '/\/$/{a=+$5;p=1}END{print p?a:\"no data\"}'",
                    "data0_use": "df -h | awk '/\/data0$/{a=+$5;p=1}END{print p?a:\"no data\"}'",
                    "var_use": "df -h | awk '/\/var$/{a=+$5;p=1}END{print p?a:\"no data\"}'",
                    "usr_use": "df -h | awk '/\/usr$/{a=+$5;p=1}END{print p?a:\"no data\"}'",
                    "tmp_use": "df -h | awk '/\/tmp$/{a=+$5;p=1}END{print p?a:\"no data\"}'",
                    "cpu_load": "/usr/bin/uptime | awk -F: '{print $NF}'"}

    def localhost(self, ip):
        self.__redis_db = RedisHash(ip,self.__name,**self.redis_options)
        result = {}
        for k,v in self.commands.items():
            data = Popen(v,shell=True,stdout=PIPE).stdout.read().strip()
            self.__redis_db.put(k,data)
            result[k] = json.dumps(data)
           
	self.__mysql_db.execute("insert into history(id,host_date,cpu_use,cpu_iowait,mem_use,swap_use,root_use,data0_use,var_use,usr_use,tmp_use,cpu_load) values(null,now(),'%s','%s','%s','%s','%s','%s','%s','%s','%s','%s')"%(result["cpu_use"],result["cpu_iowait"],result["mem_use"],result["swap_use"],result["root_use"],result["data0_use"],result["var_use"],result["usr_use"],result["tmp_use"],result["cpu_load"]))

    def remote(self, ip, passwd, stdoutMsg="", stderrMsg=""):
        self.__redis_db = RedisHash(ip,self.__name,**self.redis_options)
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(ip, 22, 'root', passwd,timeout=60)
        except Exception as e:
            self.__redis_db.put("Error","%s"%e)
	    self.__mysql_db.execute("insert into history_host values(null,'%s',now(),'%s',0,0,0,0,0,0,0,0,0,0)"%(ip,'Error: %s'%e))
            raise e
        
        result = {}
        for k,v in self.commands.items():
            stdin,stdout,stderr = ssh.exec_command(v)
            data = stdout.read().strip()+stderr.read().strip()
            self.__redis_db.put(k,data)
            result[k] = json.dumps(data)
            
	self.__mysql_db.execute("insert into history_host(id,host_ip,host_date,cpu_use,cpu_iowait,mem_use,swap_use,root_use,data0_use,var_use,usr_use,tmp_use,cpu_load) values(null,'%s',now(),'%s','%s','%s','%s','%s','%s','%s','%s','%s','%s');"%(ip,result["cpu_use"],result["cpu_iowait"],result["mem_use"],result["swap_use"],result["root_use"],result["data0_use"],result["var_use"],result["usr_use"],result["tmp_use"],result["cpu_load"]))

def host_get_local():
    hg.localhost("localhost")


def host_get_remote():
    db = torndb.Connection('127.0.0.1','cpis','root','cine123456',charset='utf8',connect_timeout=60,time_zone='+8:00')
    for i in db.query("select cinema_ip,cinema_passwd from cinema_ty"):
        hg.remote(i["cinema_ip"],i['cinema_passwd'])

def err_listener(ev):    
    db = torndb.Connection('127.0.0.1','cpis','root','cine123456',charset='utf8',connect_timeout=60,time_zone='+8:00')
    if ev.exception:    
       	db.execute("insert into errors values(null,'%s error');"%str(ev.job))    
    else:    
        db.execute("insert into logs values(null,'%s miss');"%str(ev.job))

if __name__ == '__main__':
    db = torndb.Connection('127.0.0.1','cpis','root','cine123456',charset='utf8',connect_timeout=60,time_zone='+8:00')
    hg = Host_Get("host",db)
    scheduler = TornadoScheduler(executors={'default': ThreadPoolExecutor(20)})
    store = RedisJobStore(db=3,
                          password="!a@b#c4d",
                          jobs_key="host.jobs",
                          run_times_key="host.run_times")
    scheduler.add_jobstore(store)
    scheduler.add_listener(err_listener, apscheduler.events.EVENT_JOB_ERROR | apscheduler.events.EVENT_JOB_MISSED)
    if len(sys.argv) > 1 and sys.argv[1] == '--clear':
        scheduler.remove_all_jobs()
    scheduler.add_job(host_get_local,'interval',minutes=15,misfire_grace_time=5,max_instances=5)
    scheduler.add_job(host_get_remote,'interval',minutes=30,misfire_grace_time=20,max_instances=30)
    scheduler.start()

    try:
        IOLoop.instance().start()
    except (KeyboardInterrupt, SystemExit):
        pass

