#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 14 13:10:41 2018

@author: liu
"""

import requests
import time
from bs4 import BeautifulSoup as Bs
from requests.adapters import HTTPAdapter
from urllib import request 
import wget
import os
import asyncio
from settings import head, proxies



def Get_page(page_address, max_retry=3):
    pic_page = None
    while max_retry:
        try:
            with requests.Session() as requested:
                requested.mount('https://', HTTPAdapter(max_retries=2))
                requested.mount('http://', HTTPAdapter(max_retries=2))
                pic_page = requested.get(page_address, headers=head, timeout=8)
                break
#        except ConnectionError as e:
        except:
            max_retry -= 1
            time.sleep(3)
    if not pic_page:
        raise Exception("connection error!")
    pic_page.encoding = 'utf-8'
#    print(pic_page.text)
    text_response = pic_page.text
    content = Bs(text_response, 'lxml')
    
    return content

def Download_img(page_address, agent=False):
    requested = requests.Session()
    requested.mount('https://', HTTPAdapter(max_retries=3))
    requested.mount('http://', HTTPAdapter(max_retries=3))
    pic_content = requested.get(page_address, headers=head, proxies=None, timeout=8).content
    if agent:
        pic_content = requested.get(page_address, headers=head, proxies=proxies, timeout=8).content
    return pic_content


class downloader:
    def __init__(self, url, download_to, max_block_size=1024*1024, thread_num=0, agent=False):
        self.url = url
        self.name = download_to
        self.headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'}
        req = request.Request(self.url, headers=self.headers)
        response = request.urlopen(req)
        file_size = response.getheader('Content-Length')
        self.total = int(file_size)
        if thread_num:
            self.thread_num = thread_num-1
        else:
            self.thread_num = (self.total+max_block_size-1)//max_block_size-1
        self.agent = agent

#        print('File size is %d KB'%(self.total/1024))

    # 划分每个下载块的范围
    def get_range(self):
        ranges=[]
        offset = self.total//(self.thread_num+1)
        for i in range(0, self.total, offset):
            if i == (self.thread_num)*offset:
                ranges.append((i,self.total))
            else:
                ranges.append((i,i+offset-1))
        return ranges

    async def download(self,start,end, event_num):
        post_data = {'Range':'Bytes=%s-%s' % (start,end),'Accept-Encoding':'*'}
        post_data['user-agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
        # headers = urllib.urlencode(post_data)
        res_get = lambda:requests.get(self.url, headers=post_data, proxies=None)
        if self.agent:
            res_get = lambda:requests.get(self.url, headers=post_data, proxies=proxies)
        loop = asyncio.get_event_loop()
        res = await loop.run_in_executor(None, res_get)
        self.fd.seek(start,0)
        self.fd.write(res.content)
#        print("Number[%d] block was written"%event_num)


    def run(self):
        open(self.name, 'w').close() #这句话必须有，不能省略然后底下用ab，原因似乎跟创建文件后指针才能自由移动有关
        with open(self.name,'rb+') as self.fd:
            loop = asyncio.get_event_loop()
            thread_list = []
            n = 1
            for ran in self.get_range():
                start,end = ran
#                print(start, end)
                dd = self.download(start, end, n)
                thread_list.append(dd)
                n += 1
            loop.run_until_complete(asyncio.gather(*thread_list))
#            loop.run_until_complete(asyncio.wait(thread_list))
#            loop.close()
#            print('download success')
            
def time_deco(func):
    def wrapper(*args, **kwargs):
        startTime = time.time()
        func(*args, **kwargs)
        endTime = time.time()
        msecs = (endTime - startTime)*1000
        print("time is %d ms" %msecs)
    return wrapper
 
#@time_deco           
def myDownload(src, filepath, mode=2, thread_num=10):
    if mode==1: #单线程下载，目前最快
        img_file = Download_img(src)
        with open(filepath, 'wb') as file:
            file.write(img_file)
    elif mode==2: #多协程下载，比多线程强，实测挺水
        dfile = downloader(src, filepath, thread_num=thread_num)
        dfile.run()
    else: #易被封锁
        [dirname, _] = os.path.split(filepath)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        wget.download(src, out=filepath)
        
