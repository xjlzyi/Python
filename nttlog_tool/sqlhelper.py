#!/usr/bin/env python2.7
# -*- coding:utf-8 -*-
import MySQLdb

class SqlHelper(object):
    conn = None

    def __init__(self):
        self.conn = MySQLdb.connect(host="106.15.50.59",port=5306,user="hhw",passwd="Aa123456",db="permiss")

    def __del__(self):
        self.conn.close()

    def init_connect(self):
        pass
        # cur = conn.cursor()
        # count = cur.execute("select * from action")
        # print(count)

    def test(self):
        cur = self.conn.cursor()
        count = cur.execute("select * from actor")
        cur.close()
        # print count

    def close_conn(self):
        self.conn.close()
    