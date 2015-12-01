#!/usr/bin/python
#-*- coding:utf-8 -*-

#funtion: a simple tcp server
__author__ = 'pandaychen'

import socket
import logging
import select
import errno
import signal
import sys
import time
import Queue
import os


g_serverip = "127.0.0.1"
g_serverport = 8887
MAX_TCP_BUFFER =2048


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

def TcpServerBinder(t_serverip,t_serverport):
    try:
        listenfd = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
    except socket.errno,e:
        LoggingFun("tcp_serever_log","create tcp socket error")

    listenfd.setblocking(False)

    try:
        listenfd.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    except socket.errno,e:
        LoggingFun("tcp_serever_log","set tcp socket error")

    try:
        if t_serverip is None:
            server_addr = ('',int(t_serverport))
            listenfd.bind(server_addr)
        else:
            server_addr = (t_serverip,t_serverport)
            listenfd.bind(server_addr)
    except socket.errno,e:
        LoggingFun("tcp_serever_log","bind tcp socket error")

    listenfd.listen(10)

    return listenfd


def SelectServerLoop(t_listenfd,t_client_iplist,t_all_msg_queue,t_timeout_dict):

    if t_listenfd is None:
        LoggingFun("tcp_serever_log","t_listenfd None")
        sys.exit(1)
    else:
        #将监听fd加入集合(等待读)
        select_inputs = [t_listenfd]
        #等待写集合
        select_outputs = []
        timeout =30

        while True:
            #waiting for trigger

            now = time.time()
            for key in t_timeout_dict.keys():
                if(now - t_timeout_dict[key] > 10):
                    msg = "client "+str(key)+"is delete at " +str(t_timeout_dict[key])
                    LoggingFun("tcp_serever_log",msg)
                    #del t_timeout_dict[key]    #warning!do not use this in iteration
                    t_timeout_dict.pop(key)

            readable = []
            writable = []
            exceptional = []
            readable,writable,exceptional = select.select(select_inputs,select_outputs,select_inputs,timeout)
            if not (readable or writable or exceptional):
                #no trigger
                continue;
            #loop in readable
            for sock in readable:
                if sock is t_listenfd:
                    client_connectfd,client_addr = sock.accept()
                    if t_client_iplist.has_key(client_addr[0]):
                        msg = "get connection from client:"+ str(client_addr)
                        LoggingFun("tcp_serever_log",msg)
                        #白名单client列表
                        pass
                    else:
                        continue
                    client_connectfd.setblocking(False)
                    #将连接加入select可读事件监听队列中
                    select_inputs.append(client_connectfd)
                    #add to timeout queue
                    t_all_msg_queue[client_connectfd.fileno()] = Queue.Queue()
                    #client_addr(ip,port) 一个端口一个连接
                    if t_timeout_dict.has_key(client_addr) == False:
                        t_timeout_dict.setdefault(client_addr,time.time())
                else:
                    #other socket,readable
                    recv_data = sock.recv(MAX_TCP_BUFFER)
                    #here not use recv_data is not None!
                    if recv_data:
                        #print "recv_data:",recv_data,"client:",sock.getpeername()
                        #put recv data in queue
                        t_all_msg_queue[sock.fileno()].put(recv_data)
                        if sock not in select_outputs:
                            #add s in write
                            select_outputs.append(sock)

                        if t_timeout_dict.has_key(sock.getpeername()):
                            t_timeout_dict[sock.getpeername()] = time.time()

                    else:
                        #recv error,shut down
                        msg = "delete from client",sock.getpeername()
                        LoggingFun("tcp_serever_log",msg)
                        if sock in select_outputs:
                            select_outputs.remove(sock)
                        select_inputs.remove(sock)

                        #delete from msg queue
                        if t_all_msg_queue.has_key(sock.fileno()):
                            del t_all_msg_queue[sock.fileno()]
                        if t_timeout_dict.has_key(sock.getpeername()):
                            del t_timeout_dict[sock.getpeername()]

                        #must in the last pos
                        sock.close()
            #loop in writable
            for sock in writable:
                try:
                    send_msg = t_all_msg_queue[sock.fileno()].get_nowait()
                except Queue.Empty:
                    LoggingFun("tcp_serever_log","sending msg none error")
                    select_outputs.remove(sock)
                else:
                    #sending back to client
                    #sock.getpeername()
                    sock.send(send_msg)

            #loop in exceptional
            for sock in exceptional:
                err_msg = "connection exception"+ s.getpeername()
                LoggingFun("tcp_serever_log",err_msg)
                if sock in select_outputs:
                    select_outputs.remove(sock)
                select_inputs.remove(sock)

                if t_all_msg_queue.has_key(sock.fileno()):
                    del t_all_msg_queue[sock.fileno()]
                if t_timeout_dict.has_key(sock.getpeername()):
                    del t_timeout_dict[sock.getpeername()]
                sock.close()




if __name__ == "__main__":
    client_iplist = {}
    client_iplist.setdefault("127.0.0.1",1)
    all_msg_queue={}
    timeout_dict={}
    listenerfd = TcpServerBinder(g_serverip,g_serverport)

    SelectServerLoop(listenerfd,client_iplist,all_msg_queue,timeout_dict)
