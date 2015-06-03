#!/usr/bin/env python
# -*- coding:utf8 -*-
# 定时任务脚本

import sys
import json
import logging
import paramiko
import torndb

from datetime import datetime
from tornado.ioloop import IOLoop
from apscheduler.schedulers.tornado import TornadoScheduler
from apscheduler.jobstores.redis import RedisJobStore
from apscheduler.executors.pool import ProcessPoolExecutor

logging.basicConfig(level=logging.INFO,
                format='%(asctime)s,%(filename)s,%(levelname)s,%(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename='logs/command.log',
                filemode='a+')

def apscheduler_command(host_ip,passwd,command):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    try:
        ssh.connect(host_ip,22,'root',passwd)
    except Exception as e:
        return json.dumps({'Data':'%s'%e, 'Code': 3})
    _,stdout,stderr = ssh.exec_command(command)
    outMsg = stderr.read().strip()
    if outMsg:
        return json.dumps({'Data': outMsg, 'Code': 3})
    outMsg = stdout.read().strip()
    return json.dumps({'Data': outMsg, 'Code': 3})

def ap_run(task_name,host_ip,command):
    db = torndb.Connection('127.0.0.1','cpis','root','cine123456',charset='utf8',connect_timeout=60,time_zone='+8:00')
    dbd = db.get("select host_passwd from host where host_ip='{0}' limit 1;".format(host_ip))
    passwd = dbd['host_passwd']
    print 'start'
    data = json.loads(apscheduler_command(host_ip,passwd,command))
    logging.info('IP: %s, Task_name: %s, Content: %s'%(host_ip,
                                                       task_name,
                                                       data['Data']))
    db.execute("update task_command set task_status_id=%s,content='%s' where task_name='%s' and host_ip='%s' limit 1"%(data['Code'],data['Data'],task_name,host_ip))
    return data

def main():
    sched = TornadoScheduler(executors={'processpool': ProcessPoolExecutor(5)})
    store = RedisJobStore(db=6,
                          password="!a@b#c4d",
                          jobs_key="command.jobs",
                          run_times_key="command.run_times")
    sched.add_jobstore(store)
    argv = json.loads(sys.argv[1])
    for i in argv["host_ip"]:
        run_job_time = datetime.strptime(argv["task_date"],"%Y-%m-%d %H:%M:%S")
        sched.add_job(ap_run,
                      'date',
                      run_date = run_job_time,
                      id = '%s-%s'%(argv['task_name'],i),
                      args=[argv['task_name'],
                            i,
                            argv['command']],
		      misfire_grace_time=20)

    sched.start()
    try:
        IOLoop.instance().start()
    except (KeyboardInterrupt, SystemExit):
        logging.info("Script Exit Failed!")
                      

if __name__ == "__main__":
    main()
