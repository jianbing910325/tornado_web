#!/usr/bin/env python
# -*- coding:utf8 -*-
# zabbix模块

import tornado.web
import tornado.gen
import json
import requests

from index import BaseHandler
from tornado.concurrent import run_on_executor
from concurrent.futures import ThreadPoolExecutor

class ZabbixException(Exception):
    pass

class Zabbix_Api(object):
    def __init__(self,url,user="Admin",passwd="zabbix",timeout=30):
        self.url = url+"/api_jsonrpc.php"

        self.username = user
        self.password = passwd

        self.auth = ''
        self.timeout = timeout
        self.session = requests.Session()

        self.session.headers.update({"Content-Type":"application/json",
                                     "User-Agent": "Python/zabbix_api"
                                     })

    def login(self):
        self.auth = self.zabbix_request("user","login",{"user":self.username,"password":self.password})["result"]

    def zabbix_request(self,method1,method2,params=None):
        request_json = {"jsonrpc": "2.0",
                        "method": "%s.%s"%(method1,method2),
                        "params": params or {},
                        "id": self.auth and 1 or 0
                        }
        if self.auth:
            request_json.update({"auth": self.auth})
        
        response = self.session.post(self.url,
                                     data = json.dumps(request_json),
                                     timeout = self.timeout
                                     )

        response.raise_for_status()

        if not len(response.text):
            raise ZabbixException("Returns an empty response")

        try:
            response_json = response.json()
        except ValueError:
            raise ZabbixException("Unable to parse json: %s"%response.json())

        if 'error' in response_json:
            if 'data' not in response_json['error']:
                response_json['error']['data'] = "No data"
            #msg = "Error {code}: {message} , {data} while sending {json}".format(
            #    code = response_json['error']['code'],
            #    message = response_json['error']['message'],
            #    data = response_json['error']['data'],
            #    json = str(request_json))
            #raise ZabbixException(msg,response_json['error']['code'])
        return response_json

class ZabbixInterface(BaseHandler):
    executor = ThreadPoolExecutor(15)
    
    def initialize(self):
        self.zabbix_api = Zabbix_Api("http://10.100.0.41")
        self.zabbix_api.login()
        
    @tornado.web.authenticated
    @tornado.web.asynchronous
    @tornado.gen.coroutine
    def post(self,method1,method2):
        params = json.loads(self.get_argument("params"))
        data = yield self.GetData(method1,method2,params)
        self.write(json.dumps(data))
        self.finish()

    @run_on_executor
    def GetData(self,method1,method2,params):
        data = self.zabbix_api.zabbix_request(method1,method2,params)
        if data.has_key('error'):
            return data['error']['data']
        else:
            return data['result']
        

class ZabbixHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self):
        self.render("zabbix.html",
                    web_title=self.title,
                    user=self.current_user,
                    page="Zabbix操作页面")

class ZabbixMethodHandler(BaseHandler):
    @tornado.web.authenticated
    def get(self,method):
        self.render("zabbix/%s.html"%method)
