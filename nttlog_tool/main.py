#!/usr/bin/env
# -*- coding:utf-8 -*-
import os
import threading
import time
from sqlhelper import *
from httpserver import *

def find_file(file_dir):
    for root, dirs, files in os.walk(file_dir):
        for file in files:
            filepath = os.path.join(root, file)
            if not filepath.endswith('.txt'):
                continue
            f = open(filepath, 'r')
            for line in f:
                parse_content(line)
            f.close()

def parse_content(content):
    pass

def io_thread():
    try:
        sql_helper = SqlHelper()
        sql_helper.init_connect()
        i = 0
        while i < 10:
            find_file('/home/test/Desktop/tool')
            sql_helper.test()
            time.sleep(2)
            i += 1
    except Exception, e:
        print Exception, ":", e

def http_thread():
    server = HTTPServer(('', 8888), HttpHandler)
    server.serve_forever()

if __name__ == "__main__":
    # init_connect()
    # find_file('/home/test/Desktop/tool')
    # test()
    threads = []
    t = threading.Thread(target=io_thread)
    threads.append(t)
    t = threading.Thread(target=http_thread)
    threads.append(t)
    for t in threads:
        t.start()
    print "Server starting..."
    for t in threads:
        t.join()
    print "Server stoped"
