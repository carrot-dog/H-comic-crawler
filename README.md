# H-comic-crawler
多个H漫画网站图片爬取程序，目前支持的网站有：<br>
* luscious.net
* 18comic.org
* 604s.com
* nhentai.net
    

## 环境
Python3.6，需安装wget包
```python
  pip install wget
```  
需部署MySQL环境，数据库信息在settings.py中配置

## 使用
主程序为dbInfo.py，main.py 和 main2.py，运行dbInfo.py并按提示输入漫画主页（非第一页）的网址，输入空格退出输入环节。

运行main.py将列表中漫画并发爬取，以图片地址/文件路径名形式储存在数据库中<br>
运行main2.py将数据库中链接并发下载到本地，有三种下载模式可选，推荐使用第一种。下载路径在settings.py中配置。

