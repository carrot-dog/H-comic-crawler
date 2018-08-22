#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 16 16:41:38 2018

@author: liu

Python有GIL锁，多线程无法充分利用多核性能，所以使用多进程
"""

from comics.spider_module import Pic_saver
import multiprocessing

if __name__ =="__main__":
    
    processnum = multiprocessing.cpu_count()
    processes = []
    for i in range(processnum):
        processes.append(multiprocessing.Process(target=Pic_saver))
    
    for p in processes:
        p.start()
