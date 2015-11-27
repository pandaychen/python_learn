#!/usr/bin/env python
#-*-encoding:utf-8-*-

#进程队列的使用sample

import multiprocessing
import time
import  threading

#继承threading.Thread
class ThreadConsumer(threading.Thread):
    pass

#继承multiprocessing.Process类
class Consumer(multiprocessing.Process):

    def __init__(self, task_queue, result_queue):
        multiprocessing.Process.__init__(self)
        self.task_queue = task_queue    #任务队列
        self.result_queue = result_queue    #结果队列

    #类似于threading.Thread
    def run(self):
        proc_name = self.name
        while True:
            next_task = self.task_queue.get()    #阻塞取(默认为block/True)
            if next_task is None:               #进程结束标志
                # Poison pill means shutdown
                print ('%s: Exiting' % proc_name)
                self.task_queue.task_done()
                break
            print ('%s: %s' % (proc_name, next_task))
            answer = next_task() # __call__()
            self.task_queue.task_done()     #当前的任务已经完成
            self.result_queue.put(answer)   #将结果放入结果队列
        return


#构造用于计算的对象
class Task(object):
    def __init__(self, a, b):
        self.a = a
        self.b = b
    def __call__(self):     #()   ===> for call
        time.sleep(0.1) # pretend to take some time to do the work
        return '%s * %s = %s' % (self.a, self.b, self.a * self.b)
    def __str__(self):
        return '%s * %s' % (self.a, self.b)

if __name__ == '__main__':
    # Establish communication queues
    #在主进程中创建队列
    tasks = multiprocessing.JoinableQueue()
    results = multiprocessing.Queue()

    # Start consumers---获取core数目
    num_consumers = multiprocessing.cpu_count()
    print ('Creating %d consumers' % num_consumers)

    #创建Consumers对象数组
    consumers = [ Consumer(tasks, results) for i in range(num_consumers) ]
    for w in consumers:
        w.start()

    # Enqueue jobs
    # 将任务放入任务队列
    num_jobs = 10
    for i in range(num_jobs):
        tasks.put(Task(i, i))       #将对象放入queue

    # Add a poison pill for each consumer
    for i in range(num_consumers):
        tasks.put(None)    #放入结束标志
    # Wait for all of the tasks to finish
    tasks.join()    #join() 阻塞直到queue中的所有的task都被处理(是JoinQueue的方法)

    # Start printing results
    while num_jobs:
        result = results.get()
        print ('Result:', result)
        num_jobs -= 1