#!/usr/bin/env python2.7
# -*- coding:utf-8 -*-

from BaseHTTPServer import HTTPServer, BaseHTTPRequestHandler
import json
import cgi
import re

class HttpHandler(BaseHTTPRequestHandler):
    request_args = []
    def do_GET(self):
        request_url = str(self.path)
        if not request_url.startswith('/api/'):
            self.send_error(404, "File not found")
            return
        index = request_url.find('?')
        method = request_url[5:index]
        self.request_args.append('method='+method)
        args = re.split('&', request_url[index+1:])
        self.request_args.extend(args)
        self.parse_url()
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write("success")

    # def do_POST(self):
    #     ctype, pdict = cgi.parse_header(self.headers['content-type'])
    #     if ctype == 'application/json':
    #         pass
    #     else:
    #         self.send_error(415, "Only json data is supported.")
    #         return

    #     self.send_response(200)
    #     self.send_header('Content-type', 'text/html')
    #     self.end_headers()
    #     self.wfile.write("success")

    def parse_url(self):
        method = self.request_args[0].split('=')[1]
        if method == "Login":
            pass
        else if method == "Create":
            pass
        pass