#!usr/bin/env python
# -*- coding:utf-8 -*-

__author__ = "pandaychen"

import Queue
import sys
import os
import threading
import time
import signal

def handler():
    print "press CTRL+C to end...."
    sys.exit(1)


def call_function(para):
    time.sleep(5)
    return para


def LoggingFun(t_filename,t_logcontent):
    logpath = './log/'
    curdate = time.strftime("%Y%m%d")
    newpath = './log/'+t_filename+'_'+curdate

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

class LogThread(threading.Thread):
    def __init__(self,logQueue,**kwds):
        threading.Thread.__init__(self,**kwds)
        self.logQueue = logQueue
        self.setDaemon(True)

    def run(self):
        while 1:
            #log = self.logQueue.get(False)
            log = self.logQueue.get()
            if log:
                LoggingFun("test",log)
                pass
            else:
                LoggingFun("test","log thread sleep 1s")
                time.sleep(1)

#封装为一个线程类
class Worker(threading.Thread):    # 处理工作请求
    def __init__(self, workQueue, resultQueue,logQueue, threadid,**kwds):
        threading.Thread.__init__(self, **kwds)
        self.setDaemon(True)
        self.workQueue = workQueue
        self.resultQueue = resultQueue
        self.logQueue = logQueue
        self.threadid = threadid

    def run(self):
        while 1:
            try:
                callable, args, kwds = self.workQueue.get(False)    # get a task
                res = callable(*args, **kwds)
                strres = "thread:"+ str(self.threadid) + " done,"+"args:"+str(res)

                self.logQueue.put(strres)
                self.resultQueue.put(res)    # put result
            except Queue.Empty:
                break

class WorkManagerPool:    # 线程池管理,创建
    def __init__(self, num_of_workers=10):
        self.workQueue = Queue.Queue()    # 请求队列
        self.resultQueue = Queue.Queue()    # 输出结果的队列
        self.logQueue = Queue.Queue()
        self.workers = []
        self._recruitThreads(num_of_workers)

    def _recruitThreads(self, num_of_workers):
        for i in range(num_of_workers):
            worker = Worker(self.workQueue, self.resultQueue,self.logQueue,i)    # 创建工作线程
            worker.setDaemon(True)
            self.workers.append(worker)    # 加入到线程队列

        logthread = LogThread(self.logQueue)
        self.workers.append(logthread)


    def start(self):
        for w in self.workers:
            w.start()

    def wait_for_complete(self):
        while len(self.workers):
            worker = self.workers.pop()    # 从池中取出一个线程处理请求
            worker.join()
            if worker.isAlive() and not self.workQueue.empty():
                self.workers.append(worker)    # 重新加入线程池中
                print 'All jobs were complete.'


    def add_job(self, callable, *args, **kwds):
        self.workQueue.put((callable, args, kwds))    # 向工作队列中加入请求

    def get_result(self, *args, **kwds):
        return self.resultQueue.get(*args, **kwds)



def main():
    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)

    try:
        num_of_threads = int(sys.argv[1])
    except:
        num_of_threads = 10
        start = time.time()
        workermanagepool = WorkManagerPool(num_of_threads)
        #print num_of_threads
        print "thread pool start...."
        urls = ['http://bbs.qcloud.com'] * 1000
        for i in urls:
            workermanagepool.add_job(call_function, i)

        workermanagepool.start()
        workermanagepool.wait_for_complete()
        print time.time() - start

if __name__ == '__main__':
    main()
