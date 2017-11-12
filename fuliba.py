#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import requests
import time
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, wait, as_completed

STORE_PATH = 'fuliba2'

def download_img(link, abspath):
    filename = os.path.basename(link)
    filepath = (os.path.join(abspath,filename))
    try:
        f = open(filepath, 'ab')
        try:
            data = requests.get(link, headers=headers).content
        except:
            time.sleep(1)
            data = requests.get(link, headers=headers).content
        try:
            f.write(data)
            f.close()
        except:
            f.close()
            pass
    except:
        fail = True
        pass

def parse_img(data):
    url = data['url']
    abspath = data['abspath']
    print ('parse_img',url)
    content = requests.get(url)
    article = BeautifulSoup(content.text, 'lxml').find('article', class_='article-content')
    imgags = article.find_all('img')
    for img in imgags:
        link = img['src']
        print('Downloading:',link)
        download_img(link,abspath)
    print('parse_img & download_img finish',url)
    return content.text



def parse_page(url,pool,abspath):
    print('parse_page', url)
    data = {'url': url, 'abspath': abspath}
    text = parse_img(data)
    if text is None:
        content = requests.get(url)
        text = content.text
    pages = BeautifulSoup(text, 'lxml').find('div', class_='article-paging')
    if pages is None:
        return
    pagelinks = pages.find_all('a')
    futures = []
    for pagelink in pagelinks:
        link = pagelink['href']
        data = {'url':link,'abspath':abspath}
        futures.append(pool.submit(parse_img,(data)))
        # parse_img(link)
    return futures


def parse_article(h2):
    if h2.find('a') is not None:
        alink = h2.find('a')
        link = alink['href']
        title = alink.get_text().strip(r'/\*:"|<> ？ ， !?()（）?（')
        if os.path.exists(title):
            print(title, 'pass')
            return
        if not os.path.exists(title):
            try:
                os.makedirs(title)
                abspath = os.path.abspath(title)
            except:
                pass
            print(title, '开始下载')
        pool = ThreadPoolExecutor(max_workers=10)
        wait(parse_page(link, pool, abspath))
        pool.shutdown()
        print('parse_artitcl finish ',title)

def parse_index(text):
    archives = BeautifulSoup(text, 'lxml').find_all('h2')
    poolG = ThreadPoolExecutor(max_workers=10)
    futuresG = []
    for h2 in archives:
        # parse_article(h2)
        futuresG.append(poolG.submit(parse_article,(h2)))
    wait(futuresG)
    poolG.shutdown()


if not os.path.exists(STORE_PATH):
    os.makedirs(STORE_PATH)
os.chdir(STORE_PATH)

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:53.0) Gecko/20100101 Firefox/53.0', 'Referer':'https://www.fxfuli.org/category/fuliba/'}
url = 'https://www.fxfuli.org/category/fuliba/page/'
page = 1
print('getting page',url+str(page))
html = requests.get(url+str(page))
while html.status_code == 200:
    print('processing page',page)
    parse_index(html.text)
    page=page+1
    print('getting page', url + str(page))
    html = requests.get(url + str(page))




