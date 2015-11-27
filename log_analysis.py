#!/usr/bin/env python
#-*-encoding:utf-8-*-

#function:解析特定格式日志,结果写入字典

__author__ = 'pandaychen'

import re
import sys
import time

#log format
#127.0.0.1 - - [28/Sep/2015:18:45:53 +0800] "GET /favicon.ico HTTP/1.1" 200 133 "-" "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:31.0) Gecko/20100101 Firefox/31.0"

def analysis_log(t_filepath):
    try:
        fd=open(t_filepath,"r")
        #create a new dict
        ipdict={}
        lines = fd.readlines()
        for line in lines:
            #生成IP的正则匹配
            ip_regex = re.compile(r'^(((2[0-4]\d|25[0-5]|[01]?\d\d?)\.){3}(2[0-4]\d|25[0-5]|[01]?\d\d?))')
            matcher = ip_regex.match(line)
            if matcher is not None:
                ip = matcher.group(1)       #取第一个匹配分组
                if(ipdict.has_key(ip)):
                    ipdict[ip]+=1
                else:
                    ipdict.setdefault(ip,1) #加入一个新的(key,value)

        fd.close()

        #print
        for tempkey in ipdict:
            print tempkey+"==>"+str(ipdict[tempkey])
    except Exception,e:
        print e
        sys.exit(-1)


def analysis_log_else(t_filepath):
    try:
        #create a new dict
        ipdict={}
        fd=open(t_filepath,"r")

        for line in fd:
            #生成IP的正则匹配
            ip_regex = re.compile(r'^(((2[0-4]\d|25[0-5]|[01]?\d\d?)\.){3}(2[0-4]\d|25[0-5]|[01]?\d\d?))')
            matcher = ip_regex.match(line)
            if matcher is not None:
                ip = matcher.group(1)       #取第一个匹配分组
                if(ipdict.has_key(ip)):
                    ipdict[ip]+=1
                else:
                    ipdict.setdefault(ip,1) #加入一个新的(key,value)

        fd.close()

        #print
        for tempkey in ipdict:
            print tempkey+"==>"+str(ipdict[tempkey])
    except Exception,e:
        print e
        sys.exit(-1)

if __name__ == "__main__":
    filepath = "./log"
    analysis_log_else(filepath)