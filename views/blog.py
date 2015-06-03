#!/usr/bin/env python
# -*- coding:utf8 -*-
# 书写文章所用

import tornado.web
import sys,json
from index import BaseHandler

class BlogHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        thead = ["标题","内容","分类","创建时间","修改时间","作者"]
        data = self.db.query("select a.blog_id,a.blog_title,\
                             a.blog_content,a.blog_group,a.blog_mtime,a.blog_ctime,\
                             b.user_name as user_id from blog a,user b where a.user_id = b.user_id;")
        self.render("blog.html",
                    web_title=self.title,
                    user=self.current_user,
                    thead=thead,
                    tbody=data,
                    page="文章列表")

class BlogACHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self,input):
        if input == 'add':
            data = self.db.query("select * from blog_group")
            self.render("blog_action.html",
                        web_title=self.title,
                        user=self.current_user,
                        page="添加文章",
                        group=data)
            
        elif input == 'edit':
            blog_id = self.get_argument('blog_id')
            data = self.db.get("select * from blog where blog_id = '%s'"%blog_id)
            group = self.db.query("select * from blog_group where blog_group \
                != ( select blog_group from blog where blog_id = '%s');"%blog_id)                 
            self.render("blog_edit.html",
                        web_title=self.title,
                        user=self.current_user,
                        page="修改文章",
                        data=data,
                        group=group)
            
        elif input == 'list':
            blog_id = self.get_argument('id')
            data = self.db.get("select a.blog_id,a.blog_title,a.blog_content,a.blog_group,\
                        a.blog_mtime,a.blog_ctime,b.user_email,b.user_name as user_id from blog a,\
                        user b where a.user_id = b.user_id and a.blog_id = '%s'"%blog_id)
            tmp = data['blog_content']
            data['blog_content'] = tmp.split("<br>")
            self.render("blog_list.html",
                        web_title=self.title,
                        user=self.current_user,
                        page="文章",
                        data=data)
            
        elif input == 'del':
            blog_id = self.get_argument('blog_id')
            num = self.db.execute_rowcount("delete from blog where blog_id = '%s'"%blog_id)
            if num:
                self.redirect("/blog")
            else:
                self.render("404.html",
                            error="文章删除失败，可能文章已经在其他客户端被删",
                            message="我们找遍整个网站都没有找到ta!")


    @tornado.web.authenticated
    def post(self,input):
        if input == 'add':
            user_id = self.db.get("select user_id from user where user_email = '%s' limit 1"%self.current_user)
	    content = self.get_argument('content').replace("'","''").replace("%","%%")
            values = (self.get_argument('title'),
                      content,
                      self.get_argument('class'),
                      user_id['user_id'])
            self.db.execute("insert into blog values(null,'%s','%s','%s',now(),now(),'%s');"%(values))
            self.redirect("/blog")
            
        if input == 'edit':
	    content = self.get_argument('content').replace("'","''").replace("%","%%")
            values = (self.get_argument('title'),
                      content,
                      self.get_argument('class'),
                      self.get_argument('rid'))
            self.db.execute("update blog set blog_title='%s',blog_content='%s',\
blog_group='%s',blog_ctime=now() where blog_id='%s' limit 1;"%(values))
            self.redirect("/blog/list?id=%s"%self.get_argument('rid'))
