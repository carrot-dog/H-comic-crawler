#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 16 10:49:56 2018

@author: liu

Python有GIL锁，多线程无法充分利用多核性能，所以使用多进程
"""

from spider_module import *
import multiprocessing

if __name__ == '__main__':
    #先以续传模式运行一遍，检查是否有中途退出的任务，并完成之
    Spider_engine(mode='c')
    processnum = multiprocessing.cpu_count()
    
#    processnum = 1
    processes = []
    for i in range(processnum):
        p = multiprocessing.Process(target=Spider_engine)
        p.start()

    
#    Spider_engine()    w
