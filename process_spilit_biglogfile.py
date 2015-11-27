#!/usr/bin/env python
#-*-encoding:utf-8-*-

__author__ = 'panday.chen'

import urlparse
import datetime
import os
from multiprocessing import Process,Queue,Array,RLock
import sys

"""
多进程分块读取文件
"""

#process count
WORKERS = 4

#block size
BLOCKSIZE = 100000000
FILE_SIZE = 0

def getFilesize(file):
    #获取要读取文件的大小
    global FILE_SIZE
    fstream = open(file,'r')
    fstream.seek(0,os.SEEK_END)
    FILE_SIZE = fstream.tell()
    fstream.close()

def process_found(pid,array,file,rlock,file_size):
    global FILE_SIZE
    global JOB
    global PREFIX
    """
        进程处理
        Args:
            pid:进程编号
            array:进程间共享队列，用于标记各进程所读的文件块结束位置
            file:所读文件名称
        各个进程先从array中获取当前最大的值为起始位置startpossition
        结束的位置endpossition (startpossition+BLOCKSIZE)
        if (startpossition+BLOCKSIZE)<FILE_SIZE else FILE_SIZE
        if startpossition==FILE_SIZE则进程结束
        if startpossition==0则从0开始读取
        if startpossition!=0为防止行被block截断的情况，先读一行不处理，从下一行开始正式处理
        if 当前位置 <=endpossition 就readline
        否则越过边界，就从新查找array中的最大值
    """
    fstream = open(file,'r')

    while True:
        rlock.acquire()
        print 'pid%s'%pid,','.join([str(v) for v in array])
        startpossition = max(array)
        endpossition = array[pid] = (startpossition+BLOCKSIZE) if (startpossition+BLOCKSIZE)<file_size else file_size
        rlock.release()

        if startpossition == file_size:#end of the file
            print 'pid%s end'%(pid)
            break
        elif startpossition !=0:
            fstream.seek(startpossition)
            fstream.readline()
        pos = ss = fstream.tell()
        ostream = open('D:\\'+str(pid)+'_jobs'+str(endpossition),'w')
        while pos<endpossition:
            #处理line
            line = fstream.readline()
            ostream.write(line)
            pos = fstream.tell()

        print 'pid:%s,startposition:%s,endposition:%s,pos:%s'%(pid,ss,pos,pos)
        ostream.flush()
        ostream.close()
        ee = fstream.tell()

    fstream.close()

def main():
    global FILE_SIZE
    print datetime.datetime.now().strftime("%Y/%d/%m %H:%M:%S")

    file = "D:\\debian-8.2.0-amd64-DVD-1.iso"
    getFilesize(file)
    print FILE_SIZE

    file_size= FILE_SIZE

    rlock = RLock()
    array = Array('l',WORKERS,lock=rlock)

    for t in array:
        print t

    sys.exit(1)

    threads=[]
    for i in range(WORKERS):
        p=Process(target=process_found, args=[i,array,file,rlock,file_size])
        threads.append(p)

    for i in range(WORKERS):
        threads[i].start()

    for i in range(WORKERS):
        threads[i].join()

    print datetime.datetime.now().strftime("%Y/%d/%m %H:%M:%S")

if __name__ == '__main__':
    main()
