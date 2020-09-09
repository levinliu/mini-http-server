#!/usr/bin/env python                                                       
# -*- coding: utf-8 -*-
"""
resolve url path as relative path
"""

import os
import posixpath
import urllib


def resolve_path(uri_path):
    path = uri_path.split('?',1)[0]
    path = path.split('#',1)[0]
    path = posixpath.normpath(urllib.unquote(path))
    words = path.split('/')
    words = filter(None,words)
    path = os.getcwd()
    for w in words:
        drive, word = os.path.splitdrive(w)
        head, word = os.path.split(word)
        print("word " , word, os.curdir, os.pardir)
        if word in (os.curdir, os.pardir):
            continue
        path = os.path.join(path, word) 
    print("resolve path", path)
    return path


if __name__ == '__main__':
    print(resolve_path("/"))
    print(resolve_path("/abc?a=0&b=1"))


