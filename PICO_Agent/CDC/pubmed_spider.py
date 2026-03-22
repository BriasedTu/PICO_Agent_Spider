#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: samsepi0l  ~For My Girl CHAO~
# time: 202401/07
# 导入需要的模块
import os
import re
import time
import requests
import threading
import random


# 代理IP地址，替换为你的代理IP
proxy = {
    # 'http': 'http://127.0.0.1:7890',
    'http': 'http://192.168.1.177:10811',
         }

# 控制并发的信号量
concurrent_semaphore = threading.Semaphore(value=2)  # 设置为允许的最大并发线程数

# 随机User-Agent列表
user_agents = [
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:76.0) Gecko/20100101 Firefox/76.0',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.25 Safari/537.36 Core/1.70.3741.400 QQBrowser/10.5.3863.400',
    'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
    'Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11',
    'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/534.16 (KHTML, like Gecko) Chrome/10.0.648.133 Safari/534.16',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/30.0.1599.101 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (Windows NT 5.1; U; en; rv:1.8.1) Gecko/20061208 Firefox/2.0.0 Opera 9.50',
    'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; en) Opera 9.50',
    'Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11',
    'Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11',
    'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/534.57.2 (KHTML, like Gecko) Version/5.1.7 Safari/534.57.2',
]

hd = {
    'User-Agent': random.choice(user_agents)  # 随机选择一个User-Agent
}


def get_paper_info(curl, local_url):
    try:
        # 在headers中加入伪造的Referer字段，以模拟浏览器请求
        hd['Referer'] = 'https://pubmed.ncbi.nlm.nih.gov/'

        cdata = requests.get(curl, headers=hd, proxies=proxy).text
        pat2_title = "<title>(.*?)</title>"
        pat3_content = '<div class="abstract-content selected".*?>(.*?)</div>'
        pat4_date = '<span class="cit">(.*?)</span>'
        title = re.compile(pat2_title, re.S).findall(cdata)
        content = re.compile(pat3_content, re.S).findall(cdata)
        date = re.compile(pat4_date, re.S).findall(cdata)
        print("当前爬取的文章是：{}  发表时间为：{}".format(title[0],date[0]))
        
        # 在标题和摘要中分别进行关键词匹配
        if key.lower() in title[0].lower() or key.lower() in content[0].lower():
            with open(local_url + "pubmed2.html", "a", encoding="utf-8") as fh:
                fh.write(str(title[0]) + ' ----' + str(date[0]) + "<br />" + str(content[0]) + "<br /><br />")
    except Exception as err:
        # print("get_paper_info error: {}".format(err))
        pass
    finally:
        concurrent_semaphore.release()  # 释放信号量


def crawl_page(query_params, local_url, page_num):
    url = "https://pubmed.ncbi.nlm.nih.gov/" + "?term=" + query_params.get("term") + "&filter=" + query_params.get("filter")  + "&page=" + str(page_num)

    data = requests.get(url, params=query_params, headers=hd, proxies=proxy).text
    pat1_content_url = '<div class="docsum-wrap">.*?<.*?href="(.*?)".*?</a>'
    content_url = re.compile(pat1_content_url, re.S).findall(data)
    threads = []
    for i in range(0, len(content_url)):
        curl = "https://pubmed.ncbi.nlm.nih.gov/" + content_url[i]
        # 获取信号量，控制并发线程数量
        concurrent_semaphore.acquire()
        thread = threading.Thread(target=get_paper_info, args=(curl, local_url))
        threads.append(thread)
        thread.start()
        time.sleep(random.uniform(1, 3))  # 随机休眠1到3秒

    for thread in threads:
        thread.join()


def extract_year_and_month(date_string):
    # 使用正则表达式匹配年份和月份
    match = re.match(r'(\d{4}) (\w+);.*', date_string)

    if match:
        year = match.group(1)
        month = match.group(2)
        return f"{year} {month}"
    else:
        return date_string


if __name__ == "__main__":
    key = input("请输入你想查找的关键字:")
    local_url = ""
    time_limit = input("请输入你想查询的时间范围(如years.2020-2024):")

    turl = "https://pubmed.ncbi.nlm.nih.gov/"
    query_params = {
        "term": key,
        "filter": time_limit
    }
    tdata = requests.get(turl, params=query_params, headers=hd, proxies=proxy).text
    pat_allpage = '<span class="total-pages">(.*?)</span>'
    allpage = re.compile(pat_allpage, re.S).findall(tdata)
    num = input("请输入想大致获取的文章篇数（总数为" + str(int(allpage[0].replace('\n        ', '').replace(',', '')) * 10) + "):")

    for j in range(0, int(num) // 10 + 1):      #实现翻页，每页10篇文章
        crawl_page(query_params, local_url, j + 1)