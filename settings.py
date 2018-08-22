#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Aug 16 09:48:23 2018

@author: liu
"""

'''
mysql settings
'''

HOST = '192.168.50.72'
PORT=33006
USER='liu'
PASSWD='3233836'
DB='comic_links'

abs_path = "/person_files/comic_downloads/"

head = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/68.0.3440.106 Safari/537.36'
                     }
proxies = { "http": "http://127.0.0.1:55402", "https": "127.0.0.1:55402"}
