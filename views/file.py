#!/usr/bin/env python
# -*- coding:utf8 -*-
# 文件上传同步模块

import tornado.web
import os
import sys
import random
import datetime
import json
from index import BaseHandler
import tornado.gen

reload(sys)
sys.setdefaultencoding("utf-8")

class UploadHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render("upload.html",
                    web_title=self.title,
                    user=self.current_user,
                    page="上传文件")

    @tornado.web.asynchronous
    def post(self):
        upload_path=os.path.join(os.getcwd(),'uploads')
        upfile_meta = self.request.files['myfile']
        for meta in upfile_meta:
            rand = random.randint(1000,9999)
            now = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
            file_name = meta['filename']
            file_name = now+str(rand)+file_name[file_name.rfind("."):]
            file_path = os.path.join(upload_path,file_name)
            with open(file_path,'wb') as up:
                up.write(meta['body'])
            self.db.execute("insert into upload_file values(null,'%s','%s','%s');"%(json.dumps(upload_path),
                                                                                    meta['filename'],
                                                                                    file_name))
        self.write(u"%s 文件上传成功"%file_name)
        self.finish()

class SyncHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        data = self.db.query("select host_name,host_ip from host;")
        upload_dict = self.db.query("select path,old_filename,new_filename from upload_file")
        for i in upload_dict:
            i["size"] = round(os.path.getsize(os.path.join(i["path"].strip('"'),
                                                           i["new_filename"]))/1024.0,2)
 
        self.render("sync.html",
                    web_title=self.title,
                    user=self.current_user,
                    page="同步文件",
                    action="",
                    ips=data,
                    upload_files = upload_dict)
