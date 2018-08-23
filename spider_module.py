#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 26 17:13:51 2018

@author: liu

本程序为
luscious.net
18comic.org
604s.com
nhentai.net
漫画爬取设计
"""

import time
from page_module import *
import pymysql
import pickle
import hashlib
from settings import *
import logging
import redis
from dbInfo import RedisWriter, RedisReader

logger = logging.getLogger()
logger.setLevel(logging.INFO) 
rq = time.strftime('%Y%m%d%H%M', time.localtime(time.time()))
logfile = rq+'.log'
fh = logging.FileHandler(logfile, mode='a') #追加模式，注意控制文件大小
fh.setLevel(logging.INFO)  # 输出到file的log等级的开关
formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
fh.setFormatter(formatter)
# 第四步，将logger添加到handler里面
logger.addHandler(fh)

pool = redis.ConnectionPool(host='localhost', password=3233836, db=1, port=6379, decode_responses=True)
rconn = redis.Redis(connection_pool=pool)

class Luscious(object):
    def __init__(self, address, comic_name):
        self.head = {'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                     'accept-encoding': 'gzip, deflate, br',
                     'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
                     'upgrade-insecure-requests': '1',
                     'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
                     }
        self.address = address
        self.content = Get_page(address)
        cover = self.content.find_all(class_="album_cover_item")[0].a['href']
        cover = "https://members.luscious.net"+cover
        self.cover = cover
        self.comic_name = comic_name

    def __del__(self): #以主页链接映射出的hash作为文件名保存当前进度
        if self.cover:
            md5 = hashlib.md5()
            md5.update(self.address.encode('utf8'))
            tstp_f = md5.hexdigest()+'.pkl'
            with open(tstp_f,'wb') as f:
                pickle.dump(tstp_f, f)
                logger.info("lus process saved!")
    
    def load_cover(self, link):
        filename = hashlib.md5(link.encode('utf8')).hexdigest()+'.pkl'
        try:
            with open(filename, 'rb') as f:
                return pickle.load(f)
        except IOError:
            logger.error("opening lus_loadfile error!")
        
    
    def getOthers(self):
        while self.cover:
            self.content = Get_page(self.cover)
            imgsrc = self.content.select_one('a[class="icon-download"]')['href']
            nexthref = self.content.select_one('a[id="next"]')['href']
            nexthref = "https://members.luscious.net"+nexthref
            if "more_like_this" in nexthref.split('/'):
                nexthref = None
            self.cover = nexthref
            filename = self.content.select_one('h1[id="picture_title"]').text + ".jpg"
            path = abs_path+self.comic_name+'/'+filename
            try:
                RedisWriter(rconn, imgsrc, path, '1')
            except:
                logger.error("%s下载插入失败" %imgsrc)


class l8Comic(object):
    def __init__(self, address, comic_name):
        self.head = {'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                     'accept-encoding': 'gzip, deflate, br',
                     'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
                     'upgrade-insecure-requests': '1',
                     'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
                     }
        self.address = address
        self.content = Get_page(address)
        cover = self.content.select('.btn-primary')[-1].get('href')
        self.key_number = cover.split('/')[2]
        cover = "https://18comic.org"+cover
        self.cover = cover
        self.comic_name = comic_name
        
    
    def getOthers(self):
        self.content = Get_page(self.cover)
        imgsrcs = self.content.find_all(class_="img-responsive-mw")
        tolist = []
        for src in imgsrcs:
            src_name = src.parent.get('id')
            full_src = "https://18comic.org/media/photos/"+self.key_number+'/'+src_name
            path = abs_path+self.comic_name+'/'+src_name
            tolist.append((full_src, path, '1'))
        try:
            RedisWriter(rconn, full_src, path, '1')
        except:
            logger.error("%s等若干下载插入失败" %full_src)

        
class G04s(object):
    def __init__(self, address, comic_name):
        self.head = {'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                     'accept-encoding': 'gzip, deflate, br',
                     'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
                     'upgrade-insecure-requests': '1',
                     'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
                     }
        self.address = address
        self.content = Get_page(address)
        self.comic_name = comic_name
        
    def getOthers(self):
        pics = self.content.select_one(".pics")
        imgsrcs = pics.find_all('li')
        cover_src = imgsrcs[0].img['src']
        cover_src.replace('2.jpg', '1.jpg')
        imgsrcs.insert(0, cover_src)
        tolist = []
        for src in imgsrcs:
            if type(src)==str:
                full_src = src
            else:
                full_src = src.img['src']
            src_name = full_src.split('/')[-1]
            path = abs_path+self.comic_name+'/'+src_name
            tolist.append((full_src, path, '1'))
        try:
            RedisWriter(rconn, tolist)
        except:
            logger.error("%s等若干下载插入失败" %full_src)
            
            
class Nhentai(object):
    def __init__(self, address, comic_name):
        self.head = {'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
                     'accept-encoding': 'gzip, deflate, br',
                     'accept-language': 'zh-CN,zh;q=0.9,en;q=0.8',
                     'upgrade-insecure-requests': '1',
                     'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
                     }
        self.address = address
        self.content = Get_page(address)
        self.page_srcs = self.content.find_all(class_="gallerythumb")
        self.comic_name = comic_name
        
#        self.cover = None
    def __del__(self): #以主页链接映射出的hash作为文件名保存当前进度
        if self.page_srcs:
            md5 = hashlib.md5()
            md5.update(self.address.encode('utf8'))
            tstp_f = md5.hexdigest()+'.pkl'
            with open(tstp_f,'wb') as f:
                pickle.dump(tstp_f, f)
                logger.info("nhentai process saved!")
    
    def load_cover(self, link):
        filename = hashlib.md5(link.encode('utf8')).hexdigest()+'.pkl'
        try:
            with open(filename, 'rb') as f:
                logger.info("load nhentai process success!")
                return pickle.load(f)
        except IOError:
            logger.error("opening nhentai loadfile error!")
    
    def getOthers(self):
        while self.page_srcs:
            page = self.page_srcs.pop(0).get('href')
            page_addr = "https://nhentai.net"+page
            content = Get_page(page_addr)
            img_src = content.select_one('.fit-horizontal').get('src')
            src_name = img_src.split('/')[-1].zfill(9) #补0方便文件名排序
            path = abs_path+self.comic_name+'/'+src_name
            try:
                RedisWriter(rconn, img_src, path, '1')
            except:
                logger.error("%s下载插入失败" %img_src)
            
        logger.info("One of nhentai download_links over!")
    



def Pic_saver():
    alive = 3
    while alive:
        try: #出队一条数据，将状态由1改为2，表明现在正在接受下载
            src, filepath, used = RedisReader(rconn)
        except:
            logger.error("a link failed when popped out!")
            continue
        if src:
            try:
                myDownload(src, filepath, mode=1) #1为requests下载，2为多协程下载，3为wget下载
                #如果下载成功，则正常出队
            except: #如果下载失败，则再次入队，留待以后下载
                RedisWriter(rconn, src, filepath, '1')
                time.sleep(6) #考虑到访问过快的可能性，适当进行休眠
        else:
            alive -= 1
            time.sleep(30)

def Spider_engine(mode='n'):
    
    conn = pymysql.connect(host=HOST,port=PORT,
                                    user=USER,password=PASSWD,
                                    db=DB,charset='utf8',
                                    )
    cursor = conn.cursor()
    sql0 = "SELECT * FROM comics WHERE status=2"
    sql1 = "UPDATE comics SET status=2, comic_id=LAST_INSERT_ID(comic_id) WHERE status=1 LIMIT 1" 
    sql2 = "SELECT * FROM comics WHERE ROW_COUNT()>0 and comic_id=LAST_INSERT_ID()"
    if mode=='c':
        try: #续传模式，先检查并处理队列里有无爬取链接到一半的页面，完成他们(只有Lus网站和nhentai有这种特性)
            cursor.execute(sql0)
            result0 = cursor.fetchall()
            logger.info("left %d items in half way" %len(result0))
        except:
            conn.rollback()
            result0 = []
        for item in result0:
            if "luscious" in item[2]:
                lus_engin = Luscious(item[2], item[1])
                lus_engin.cover = lus_engin.load_cover(item[2])
                lus_engin.getOthers()
            elif "nhentai" in item[2]:
                nhen_engin = Nhentai(item[2], item[1])
                nhen_engin.page_srcs = nhen_engin.load_cover(item[2])
                nhen_engin.getOthers()
        conn.close()
        return
    #如无，则开始新过程  
    try: #出队一条数据，将状态由1改为2，表明现在正在接受读取
        cursor.execute(sql1)
#        cursor.close()
#        cursor = conn.cursor()
        cursor.execute(sql2)
        conn.commit()
        result = cursor.fetchone()
        if not result:
            logger.warning("sql length error,no results!")

    except:
        conn.rollback()
        logger.error("get comiclinks error!")
    while result:
#        print("a loop open!")
        comic_title = result[1]; page_link = result[2]; source = result[4]
        comic_id = result[0]
        if source=="Luscious":
            lus_engin = Luscious(page_link, comic_title)
            logger.info('A Luscious start!')
            lus_engin.getOthers()
        elif source=="18comic":
            l8c_engin = l8Comic(page_link, comic_title)
            logger.info('A 18comic start!')
            l8c_engin.getOthers()
        elif source=="604s":
            G04_engine = G04s(page_link, comic_title)
            logger.info('A 604s start!')
            G04_engine.getOthers()
        elif source=="nhentai":
            nhen_engine = Nhentai(page_link, comic_title)
            logger.info('A nhentai start!')
            nhen_engine.getOthers()
        else:
            logger.error("meta source error!")
        sql_f = "UPDATE comics SET status=3, f_date=NOW() WHERE comic_id='%d'" %comic_id
        cursor.close()
        cursor = conn.cursor()
        cursor.execute(sql_f)
        conn.commit()
        cursor.close()
        cursor = conn.cursor()
        try: #出队一条数据，将状态由1改为2，表明现在正在接受读取
            cursor.execute(sql1)
            cursor.execute(sql2)
            conn.commit()
            result = cursor.fetchone()
        except:
            conn.rollback()
            logger.error("get comiclinks error!")
        if not result:
            break
    conn.close()
            

    

    
    
    
    