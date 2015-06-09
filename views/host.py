#!/usr/bin/env python
# -*- coding:utf8 -*-
# 主机模块

import tornado.web
import sys,json
from index import BaseHandler

class HostHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        thead = thead = ["编码","主机名","资产编码","主机IP","主机组","系统版本"]
        data = self.db.query("select * from host")
        self.render("host.html",
                    web_title=self.title,
                    user=self.current_user,
                    thead=thead,
                    tbody=data,
                    page="主机列表")


class HostACHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self,input):
        if input == 'add':
            data=self.db.query("select * from host_group")
            self.render("host_action.html",
                        web_title=self.title,
                        user=self.current_user,
                        page="添加主机",
                        group=data)
            
        elif input == 'edit':
            host_id = self.get_argument('id')
            data = self.db.get("select * from host where id = '%s' limit 1;"%host_id)
            group = self.db.query("select a.host_group from host_group \
                        a,host b where a.host_group != b.host_group and b.id='%s';"%host_id)
            self.render("host_edit.html",
                        web_title=self.title,
                        user=self.current_user,
                        page="修改主机",
                        data=data,
                        group=group)

    @tornado.web.authenticated
    def post(self,input):
        if input == 'add':
            values = (self.get_argument('host_name'),
                      self.get_argument('host_code'),
                      self.get_argument('host_ip'),
                      self.lock.encrypto(self.get_argument('host_passwd')),
                      self.get_argument('host_group'),
                      self.get_argument('version_sys'))
            self.db.execute("insert into host values(NULL,'%s','%s','%s','%s','%s','%s');"%(values))
            self.redirect("/host")
            
        elif input == 'edit':
            field = {"host_name": self.get_argument('host_name'),
                     "host_code": self.get_argument('host_code'),
                     "host_ip": self.get_argument('host_ip'),
                     "host_passwd": self.lock.encrypto(self.get_argument('host_passwd')),
                     "host_group": self.get_argument('host_group'),
                     "version_sys": self.get_argument('version_sys'),
                     "id": self.get_argument('rid')}
            sql = """update host set host_name = '{host_name}',
host_code='{host_code}',host_ip='{host_ip}',host_passwd='{host_passwd}',
host_group='{host_group}',version_sys='{version_sys}' where id = {id} limit 1;"""
            self.db.execute(sql.format(**field))
            self.redirect("/host")



