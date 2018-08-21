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
import threading
import wget
import os

head = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
                     }

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

def Download_img(page_address):
    requested = requests.Session()
    requested.mount('https://', HTTPAdapter(max_retries=3))
    requested.mount('http://', HTTPAdapter(max_retries=3))
    pic_content = requested.get(page_address, headers=head, timeout=8).content
    return pic_content


class downloader:
    def __init__(self, url, download_to, max_block_size=1024*30, thread_num=0):
        self.url = url
        self.name = download_to
        self.headers = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'}
        req = request.Request(self.url, headers=self.headers)
        response = request.urlopen(req)
        file_size = response.headers.getheader('Content-Length')
        self.total = int(file_size)
        # 根据要求或者块大小计算线程个数
        if thread_num:
            self.thread_num = thread_num
        else:
            self.thread_num = (self.total+max_block_size-1)//max_block_size
        print(self.thread_num)
        self.event_list = [threading.Event() for _ in range(self.thread_num)]
        self.event_list[0].set()
#        print('File size is %d KB'%(self.total/1024))

    # 划分每个下载块的范围
    def get_range(self):
        ranges=[]
        offset = self.total//self.thread_num
        for i in range(self.thread_num):
            if i == self.thread_num-1:
                ranges.append((i*offset,''))
            else:
                ranges.append((i*offset,(i+1)*offset))
        return ranges

    def download(self,start,end, event_num):
        post_data = {'Range':'Bytes=%s-%s' % (start,end),'Accept-Encoding':'*'}
        post_data['user-agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
        # headers = urllib.urlencode(post_data)
        req = request.Request(self.url, headers=post_data)
        res = request.urlopen(req)
        # res = requests.get(self.url,headers=headers)
#        print('%s:%s chunk starts to download'%(start,end))
        self.event_list[event_num].wait()
        self.fd.seek(start)
        self.fd.write(res.read())
        print("Number[%d] block was written"%event_num)
        if event_num<len(self.event_list)-1:
            self.event_list[event_num+1].set()

    def run(self):
        with open(self.name,'ab') as self.fd:
            thread_list = []
            n = 0
            for ran in self.get_range():
                start,end = ran
                print('thread %d Range:%s ~ %s Bytes'%(n, start, end))
                thread = threading.Thread(target=self.download, args=(start,end,n))
                thread.start()
                thread_list.append(thread)
                n += 1
            map(lambda thd:thd.join(), thread_list)
            print('download success')
            
def myDownload(src, filepath, mode=3):
    if mode==1:
        img_file = Download_img(src)
        with open(filepath, 'wb') as file:
            file.write(img_file)
    elif mode==2:
        dfile = downloader(src, filepath, thread_num=5)
        dfile.run()
    else:
        [dirname, _] = os.path.split(filepath)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        wget.download(src, out=filepath)
        
