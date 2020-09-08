#!/usr/bin/env python                                                       
# -*- coding: utf-8 -*-
"""
a mini http server
"""

import BaseHTTPServer
import os
from urlparse import urlparse, parse_qs
from shutil import copyfileobj

try:
    from cStringIO import StringIO
except ImportError:
    from StringIO import StringIO


WORKSPACE="/tmp"
PORT=11024


class FileServerHttpHandler(BaseHTTPServer.BaseHTTPRequestHandler):
   server_version = ""
   sys_version = ""

   #if not mimetypes.inited:
   #    mimetypes.init()
   
   def do_GET(self):
       if self.path.startswith('/cat'):
           return self.do_cat()
       else:
           fio = serve_path(self.path)
           copyfileobj(fio, self.wfile)
           self.send_response(200)
           self.send_header('Content-type', 'text/html')
           self.send_header('Content-Length', str(fio.tell()))
           self.end_headers()
           fio.close()
       

   def do_cat(self):
       self.send_response(200)
       self.send_header("Content-type", "text/html")
       self.end_headers() 
       self.wfile.write(cat(self.path))


def serve_path(fpath):
    base_path = os.getcwd()
    path = os.path.join(base_path, fpath)
    print("path=" + path)
    if os.path.isdir(path):
        for x in "index.html", "index.htm":
            x = os.path.join(path, x)
            if os.path.exists(x):
                path = x
                break    
        else:
            return list_dir(path)
    f = open(path, 'rb')
    return f
    

def list_dir(path):
    data_dir = WORKSPACE
    flist = os.listdir(data_dir)
    flist.sort(key=lambda a: a.lower())
    print("flist=" + str(flist))
    f = StringIO()
    f.write("""
<html><head><title>DEVTool</title>
</head>
<body>
<h3>Dir %s</h3><hr/>
</body>
</html>
""" % path)
    f.seek(0)
    return f 



def cat(path):
    qparams = parse_qs(urlparse(path).query)
    fpath = qparams['f'][0]
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
        data = '<p>Folder %s has %s files</p><ul>%s</ul>'%(fpath, no, data)
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


