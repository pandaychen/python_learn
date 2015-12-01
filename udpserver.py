#!/usr/bin/python
#-*- coding:utf-8 -*-

#funtion: a simple udp server
__author__ = 'pandaychen'

import socket
import logging
import select
import errno
import signal
import sys
import time
import platform

#packet receive counter
g_pktcount=0
MAX_UDP_BUFFER = 8192

def UserExit(t_signum, t_stack):
    global pktcount
    print "recv signal:",t_signum,";total count:",g_pktcount
    sys.exit(1)

def LoggingFun(t_filename,t_logcontent):
    logpath = './logger/'
    curdate = time.strftime("%Y%m%d")
    newpath = './logger/'+t_filename+'_'+curdate

    if os.path.exists(logpath):
        pass
    else:
        os.mkdir(logpath)

    try:
        filehd = open(newpath,'a+')
        newcontent = '['+str(time.strftime("%Y-%m-%d %H:%M:%S"))+']'+t_logcontent+'\n'
        filehd.writelines(newcontent)
        filehd.close()
    except Exception,e:
        pass

def SimpleUdpServerBinder(t_bindip,t_bindport):
    try:
        listenfd = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, 0)
    except socket.error, e:
        errmsg = "create sock error["+e+"]"
        LoggingFun("udpserver_error",errmsg)

    try:
        listenfd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    except socket.error, e:
        errmsg ="setsocketopt SO_REUSEADDR error["+e+"]"
        LoggingFun("udpserver_error",errmsg)

    try:
        if t_bindip is None:
            listenfd.bind(('', int(t_bindport)))
        else:
            listenfd.bind((t_bindip,int(t_bindport)))
    except socket.error, e:
        errmsg  = "bind error["+e+"]"
        LoggingFun("udpserver_error",errmsg)

    return listenfd


def SimpleUdpServerWorker(t_listenfd):
    global g_pktcount
    if t_listenfd is None:
        LoggingFun("udpserver_error","listenfd error")
        sys.exit(1)
    else:
        while True:
            #if no packet recv,then hold here
            message,client_addr = t_listenfd.recvfrom(MAX_UDP_BUFFER)
            if message is not None:
                g_pktcount = g_pktcount+1


def EpollUdpServerWorker(t_listenfd):
    global g_pktcount
    if platform.system() != "Linux":
        LoggingFun("udpserver_error","create epollfd error")
        sys.exit(1)
    try:
        #create epoll fd
        epollfd = select.epoll()
        #向epoll句柄中注册监听listenfd的可读事件
        epollfd.register(listenerfd.fileno(),select.EPOLLIN)
    except select.error,e:
        errmsg = "create epollfd error["+e+"]"

    client_address = {}
    client_data = {}

    while True:
        epolllist = epollfd.poll(1)  #未指定超时时间则为阻塞等待
        for (fd,events) in epolllist:
           if(fd == t_listenfd.fileno()):
               #if we care(listenfd)
               if select.EPOLLIN & events:
                    client_msg,client_address = t_listenfd.recvfrom(MAX_UDP_BUFFER)
                    g_pktcount = g_pktcount+1

if __name__ == "__main__":
    signal.signal(signal.SIGINT, UserExit)

    listenerfd = SimpleUdpServerBinder("127.0.0.1","8888")
    SimpleUdpServerWorker(listenerfd)
    #EpollUdpServerWorker(listenerfd)
