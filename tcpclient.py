#!/usr/bin/python
#-*- coding:utf-8 -*-

#funtion: a simple tcp client
__author__ = 'pandaychen'

import socket
import time
import logging
import sys
import errno

socket.setdefaulttimeout(5)

g_serverip = "127.0.0.1"
g_serverport = "8887"

def TcpClient(t_serverip,t_serverport):
    try:
        connectfd = socket.socket(socket.AF_INET, socket.SOCK_STREAM, 0)
    except socket.errno,e:
        print e

    try:
        server_addr=(t_serverip,int(t_serverport))
        #connectfd.connect_ex(server_addr)  #useless? it seems always go ahead without raise a exception
        connectfd.connect(server_addr)
    except socket.errno,e:
        print e

    for i in range(1,10):
        send_data = "hello server"
        if connectfd.send(send_data) != len(send_data):
            print "sending data error"
            break
        recv_data = connectfd.recv(1024)
        print "recv data from server:",recv_data
        time.sleep(1)

    #add this loop to simulate server's timeout
    while True:
        time.sleep(1)

    connectfd.close()

if __name__ == "__main__":
    TcpClient(g_serverip,g_serverport)
