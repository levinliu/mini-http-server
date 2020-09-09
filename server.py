#!/usr/bin/env python                                                       
# -*- coding: utf-8 -*-
"""
a mini http server
"""

import BaseHTTPServer
import os
from urlparse import urlparse, parse_qs
from shutil import copyfileobj
import mimetypes
import re

from path_util import resolve_path

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO


WORKSPACE="/tmp"
PORT=11024


class FileServerHttpHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    server_version = ""
    sys_version = ""

    if not mimetypes.inited:
        mimetypes.init()

    def render(self, content, code=200):
        io = StringIO()
        io.write(content)
        len = io.tell()
        io.seek(0)
        self.render_io(io, len, code)

    def render_io(self, io, len=0, code=200):
        self.send_response(code)
        self.send_header('Content-type', 'text/html')
        if len > 0 :
            self.send_header('Content-Length', len)
        self.end_headers()
        try:
            copyfileobj(io, self.wfile)
        finally:
            io.close()
   
    def do_GET(self):
        content = "404 Not Found"
        if self.path.startswith('/cat'):
            content = cat(self.path)
        else:
            return self.render_io(serve_path(self.path))
        self.render(content)

    def do_POST(self):
        status = True 
        msg = "NA"
        if self.path == '/upload':
             (status, msg) = self.upload()
        content = """<html><title>MiniServer</title>
<body><h3>Status</h3><h4>%s</h4>%s</body></html>"""
        content = content % ( "OK" if status else "FAILED" , msg)
        self.render(content)

    def upload(self):
        file = self.rfile
        boundary = self.headers.plisttext.split("=")[1]
        print(" boundary = ",boundary)
        bytes = int(self.headers['content-length'])
        line = file.readline() #boundary
        if not boundary in line:
            return (False, "Content Not Begin with Boundary")
        bytes -= len(line)
        line = file.readline()
        bytes -= len(line)
        fn = re.findall(r'Content-Disposition.*name="file"; filename="(.*)"', line)
        if not fn:
            return (False, "Cannot resolve file name")
        data_dir = WORKSPACE
        fn = os.path.join(data_dir, fn[0])
        line = file.readline()
        bytes -= len(line)
        line = file.readline()
        bytes -= len(line)
        try:
            out = open(fn, 'wb')
        except IOError:
            return (False, "Cannot write any file")
        preline = file.readline() #check preline to avoid '\r' issue
        bytes -= len(preline)
        while bytes >0:
            line = file.readline()
            if boundary in line:
                preline = preline[0:-1]
                preline = preline[0:-1] if '\r' in preline else preline
                out.write(preline)
                out.close()
                return (True, "File %s Uploaded" % fn)
            bytes -= len(line)
            out.write(preline)
            preline = line
        return (False, "Unknown issue on saving data")
        

def serve_path(fpath):
    path = resolve_path(fpath)
    print("serve path=" + path)
    if os.path.isdir(path):
        for x in "index.html", "index.htm":
            x = os.path.join(path, x)
            print("search index ", x)
            if os.path.exists(x):
                path = x
                break    
        else:
            return list_dir(path)
    f = open(path, 'rb')
    return f
    

def list_dir(path):
    #data_dir = WORKSPACE
    data_dir = path
    flist = os.listdir(data_dir)
    flist.sort(key=lambda a: a.lower())
    print("flist=" + str(flist))
    file_html = ''.join('<li><a href="/cat?f='+os.path.join(data_dir,x)+'" target=_blank>'+x+'</a></li>' for x in flist)
    f = StringIO()
    f.write("""
<html><head><title>MiniServer</title>
</head>
<body>
<h3>Dir %s</h3><hr/>
<p>
<form enctype="multipart/form-data" method="post" action="/upload">
<input name="file" type="file" />
<input type="submit" value="upload"/>
</form>
</p><hr/>
<p><ul>%s</ul></p>
</body>
</html>
""" % (path, file_html))
    f.seek(0)
    return f 


def cat(path):
    qparams = parse_qs(urlparse(path).query)
    fpath = qparams['f'][0] if 'f' in qparams else '.'
    return cat_file(fpath) 


def cat_file(fpath):
    data = "FileNotFound: '%s' " % fpath
    if not os.path.exists(fpath):
        return data
    if os.path.isdir(fpath):
        files = os.listdir(fpath)
        files.sort()
        no = str(len(files))
        data = ''.join('<li><a href="/cat?f='+ fpath + '/'+ x +'">'+ x +'</a></li>' for x in files)
        data = '<p>Dir [%s] has %s files</p><ul>%s</ul>'%(fpath, no, data)
    else:
        with open(fpath, 'r') as f:
            data = f.read()
            #data = data.replace('\r\n','<br/>').replace('\n','<br/>')
            data = '<pre>' + data + '</pre>'
    return data


def boot_prd():
    server_address = ('0.0.0.0', 58000)
    server_class = BaseHTTPServer.HTTPServer
    handler_class = FileServerHttpHandler
    httpd = server_class(server_address, handler_class)
    httpd.serve_forever()


if __name__ == '__main__':
    boot_prd()


