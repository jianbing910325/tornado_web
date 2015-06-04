#!/usr/bin/env python
# -*- coding:utf8 -*-

from Crypto.Cipher import AES
from binascii import b2a_hex,a2b_hex

class Locker(object):
    def __init__(self,key1,key2):
        self.key1 = key1
        self.key2 = key2
        self.mode = AES.MODE_CBC

    def encrypt(self,string):
        obj = AES.new(self.key1,self.mode,self.key2)
        length = 16
        count = len(string)
        if count < length:
            d = (length-count)
            string += '\0'*d
        elif count > length:
            d = (length-(count%length))
            string += '\0'*d
        encrypt_string = obj.encrypt(string)
        return b2a_hex(encrypt_string)

    def decrypt(self,string):
        obj = AES.new(self.key1,self.mode,self.key2)
        decrypt_string = obj.decrypt(a2b_hex(string))
        return decrypt_string.rstrip('\0')
