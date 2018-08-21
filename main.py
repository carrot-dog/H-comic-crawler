#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 16 10:49:56 2018

@author: liu

Python有PIL锁，多线程无法充分利用多核性能，所以使用多进程
"""

from spider_module import *
import multiprocessing
import time

if __name__ == '__main__':
    #先以续传模式运行一遍，检查是否有中途退出的任务，并完成之
#    Spider_engine(mode='c')
    '''
    processnum = multiprocessing.cpu_count()
    p = multiprocessing.Pool(processnum)
    for i in range(processnum):
        p.apply_async(Spider_engine,args=('n',))
    p.close()
    p.join()
    print("all processes over~")
    '''
    processnum = multiprocessing.cpu_count()
    processes = []
    for i in range(processnum):
        p = multiprocessing.Process(target=Spider_engine)
        processes.append(p)
    
    for p in processes:
        p.start()
#        p.join()
#        time.sleep(2)
#    Spider_engine()    
