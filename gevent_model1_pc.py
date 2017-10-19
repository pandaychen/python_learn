#coding=utf-8

__author__='pandaychen'

#使用多进程+gevent实现生产者-消费者模型
#多进程之间通信采用joinablequeue
 
 
from multiprocessing import Process, cpu_count, Queue, JoinableQueue
import gevent
import datetime
from Queue import Empty
import time
import sys
import os

from gevent import monkey
monkey.patch_all()


class GeConsumer(object):
    def __init__(self, t_taskqueue, t_consumer_num, t_consumer_name):
        self._taskqueue = t_taskqueue       #任务队列
        self._consumer_num = t_consumer_num
        self._consumer_name = t_consumer_name
        self.jobgidlist=[]
        self._consumer_work()
 
    def _consumer_work(self):
        for index in xrange(self._consumer_num):
            gid=gevent.spawn(self._consumer_callback)
            self.jobgidlist.append(gid)

        ##wait for end
        gevent.joinall(self.jobgidlist)

 
    def _consumer_callback(self):
        while True:
            value = self._taskqueue.get()
            if value ==None:
                #trick
                self._taskqueue.task_done()
                break
            else:
                print "[CONSUMER]recv:",value
                pass

        return


class GeProducer(object):
    def __init__(self, t_taskqueue, t_producer_num, t_producer_name, t_consumer_num):
       self._taskqueue = t_taskqueue
       self._producer_num = t_producer_num
       self._producer_name = t_producer_name
       self._consumer_num = t_consumer_num
       self.jobpidlist=[]
       #start producer
       self._producer_work()


    def _producer_work(self):
        for index in xrange(self._producer_num):
            #create a gevent in each process
            gid=gevent.spawn(self.producer_callback)
            print "geventid=",gid
            self.jobpidlist.append(gid)

        #wait for all process done
        gevent.joinall(self.jobpidlist)

        for index in xrange(self._consumer_num):
            #nofity all consumer to exit
            self._taskqueue.put_nowait(None)

        self._taskqueue.close()


    def producer_callback(self):
        while True:
            print "[PRODUCER]start a new round.."+"PID="+str(os.getpid())
            ##CTRL+C TO END
            for jobid in xrange(30):
                self._taskqueue.put(jobid, block = False)
            time.sleep(5)
        return 


def test_main():
    total_processes = cpu_count()
    jbqueue = JoinableQueue()

    ##num
    producer_gevents_num=1
    consumer_gevents_num=10

    jobs_list = []
    start = datetime.datetime.now()
    p = Process(target = GeProducer, args=(jbqueue, producer_gevents_num,"producer %d"%1, consumer_gevents_num))
    p.start()
    jobs_list.append(p)

    for x in xrange(consumer_gevents_num):
        q = Process(target = GeConsumer, args=(jbqueue, consumer_gevents_num,"consumer %d"%x))
        q.start()
        jobs_list.append(q)

    for job in jobs_list:
        job.join()
 
 
if __name__ == '__main__':
    test_main()
 
