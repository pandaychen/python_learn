#!/usr/bin/python
#-*- coding:utf-8 -*-

#funtion: a simple udp client
__author__ = 'pandaychen'

import socket
import logging
import select
import errno
import socket
import sys
import time
import signal
import sys

g_serverhost = "127.0.0.1"
g_serverport = 8888

#packet receive counter
g_pktcount=0

def UserExit(t_signum, t_stack):
    global pktcount
    print "recv signal:",t_signum,";total count:",g_pktcount
    sys.exit(1)

def UdpClient(t_serverip,t_serverport):
    global g_pktcount
    server_addr = (t_serverip,t_serverport)

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        port = int(t_serverport)
    except ValueError:
        port = socket.getservbyname(port, 'udp')

    sock.connect((t_serverip, port))

    while True:
        g_pktcount = g_pktcount+1
        data = "the "+str(g_pktcount)+"st packet"
        sock.sendto(data, server_addr)
        #time.sleep(1)

if __name__ == "__main__":
    #register
    signal.signal(signal.SIGINT, UserExit)
    UdpClient(g_serverhost,g_serverport)
