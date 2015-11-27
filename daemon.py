#!/usr/bin/env python
#-*-encoding:utf-8-*-

#function:将一个脚本放在后台运行
#杀死:kill -9 pid

import time
import sys
import platform
import os

def RealWorker():
    #业务逻辑在此
    fd = open('/tmp/tmp.log', 'w')
    while True:
        fd.write(time.ctime()+'\n')
        fd.flush()
        time.sleep(2)
    fd.close()

def Daemon():

    #一次fork
    try:
        if os.fork() > 0:
            os._exit(0)
    except OSError, error:
        print 'fork #1 failed: %d (%s)' % (error.errno, error.strerror)
        os._exit(1)

    os.chdir('/')
    os.setsid()
    os.umask(0)

    #二次fork
    try:
        pid = os.fork()
        if pid > 0:
            print 'Daemon PID %d' % pid
            os._exit(0)
    except OSError, error:
        print 'fork #2 failed: %d (%s)' % (error.errno, error.strerror)
        os._exit(1)
		
    # 重定向标准IO
    sys.stdout.flush()
    sys.stderr.flush()
    si = file("/dev/null", 'r')
    so = file("/dev/null", 'a+')
    se = file("/dev/null", 'a+', 0)
    os.dup2(si.fileno(), sys.stdin.fileno())
    os.dup2(so.fileno(), sys.stdout.fileno())
    os.dup2(se.fileno(), sys.stderr.fileno())

    # 在子进程中执行业务逻辑
    RealWorker()

def main():
    if platform.system() == "Linux":
        Daemon()
    else:
        os._exit(0)

if __name__ == '__main__':
    main()
