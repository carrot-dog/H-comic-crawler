#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug 14 13:16:54 2018

@author: liu
"""

from bs4 import BeautifulSoup as Bs
from page_module import *
import pymysql
import signal
from settings import *
import redis

is_exit = False

def RedisWriter(rconn, src, path, used, listname='download_links'):
    savestr = "湮".join([src, path, used]) #redis只能储存字符串，所以把信息拼成字符串，用的时候再分割
    rconn.lpush(listname, savestr)
def RedisReader(rconn, listname='download_links'):
    savestr = rconn.rpop(listname) #按队列方式读取，先入先出
    if savestr:
        [src, path, used] = savestr.split("湮")
        return src, path, used
    else:
        return None,None,None
    

def dbWriter(title, page_link, status, source, lang):
    conn = pymysql.connect(host=HOST,port=PORT,
                                    user=USER,password=PASSWD,
                                    db=DB,charset='utf8',
                                    )
    cursor = conn.cursor()
    sql_insert = "INSERT INTO comics (comic_title, page_link, status, source, i_date, language)\
        VALUES ('%s','%s','%d','%s', NOW(),'%s')"%\
        (title, page_link, status, source, lang)
    try:
        cursor.execute(sql_insert)
        conn.commit()
    except:
        conn.rollback()
        raise Exception("insert error!")
    conn.close()

class dbInfo(object):
    def __init__(self):
        pass
            
    def engineLuscious(self, address):
        content = Get_page(address)
        lang = content.select('meta[name="keywords"]')
        if lang:
            key_words = lang[0]['content'].split(',')
            if 'chinese' in key_words:
                lang = "CN"
            else:
                lang = None
                
        title = content.find_all(class_="markdown")[0].find_all('p')[-1].text
        title = title.split(': ')[1]

        source = "Luscious"
        
        page_link = address
        
        dbWriter(title, page_link, 1, source, lang)
            
    def engine18Comic(self, address):
        content = Get_page(address)
        title = content.select_one("div[itemprop='name']").text[1:-1]
        lang = "CN"
        source = "18comic"
        
        page_link = address
        
        dbWriter(title, page_link, 1, source, lang)
            
    def engine604S(self, address):
        content = Get_page(address)
        title = content.select_one('meta[name="Keywords"]')['content']
        lang = "CN"
        source = "604s"
        
        page_link = address
        dbWriter(title, page_link, 1, source, lang)
            
    def engineNhentai(self, address):
        content = Get_page(address)
        title = content.select_one('h2').text
        ifcn = content.find_all(text="chinese ")
        if ifcn:
            lang = "CN"
        else:
            lang = None
        source = "nhentai"
        page_link = address
        dbWriter(title, page_link, 1, source, lang)

    def engineSwitch(self, address):
        if "luscious" in address:
            self.engineLuscious(address)
        elif "18comic" in address:
            self.engine18Comic(address)
        elif "604s" in address:
            self.engine604S(address)
        elif "nhentai" in address:
            self.engineNhentai(address)
        else:
            print("address error!")
            
def handler(signum, frame):
    global is_exit
    is_exit = True
    print("input over!")
    


if __name__ == "__main__":
    signal.signal(signal.SIGINT, handler)
    signal.signal(signal.SIGTERM, handler)
    try:
        dbinfo = dbInfo()
        while not is_exit:
            addr = input("comic Page address (a backspace to stop):")
            if addr==' ':
                raise Exception("input over!")
            else:
                dbinfo.engineSwitch(addr)
    except:
        print("just stoped!")
 


    
    
    
    