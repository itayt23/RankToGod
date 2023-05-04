from typing import ParamSpec
import pandas as pd
from bs4 import BeautifulSoup
import requests
import subprocess
import p123api
import pandas as pd
from datetime import date
import random
from lxml.html import fromstring
from itertools import cycle
import traceback
import time

class AntiScrapper:
    headers = {}
    proxy = None
    proxies = []

    def __init__(self) -> None:
        pass


    def agent_maker(self):
        user_agent_list = [
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Safari/605.1.15',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:77.0) Gecko/20100101 Firefox/77.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:77.0) Gecko/20100101 Firefox/77.0',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36',
        ]
        for i in range(1,4):
        #Pick a random user agent
            user_agent = random.choice(user_agent_list)
        headers = {'User-Agent': user_agent}
        return headers

    def get_proxies(self):
        #proxies_file = open('http_proxies.txt', 'r')
        proxies_file = open('proxies.txt', 'r')
        proxies = proxies_file.readlines()
        for line in proxies:
            self.proxies.append(line.strip('\n'))


    def scrap_proxies(self):
        url = 'https://free-proxy-list.net/'
        response = requests.get(url)
        parser = fromstring(response.text)
        proxies_list = set()
        for i in parser.xpath('//tbody/tr')[:20]:
            if i.xpath('.//td[7][contains(text(),"yes")]'):
                #Grabbing IP and corresponding PORT
                proxy = ":".join([i.xpath('.//td[1]/text()')[0], i.xpath('.//td[2]/text()')[0]])
                proxies_list.add(proxy)
        proxy_pool = cycle(proxies_list)

    def rotate_proxies(self):
        self.get_proxies()
        #proxies = {"http": 'http://154.236.162.34:1981', "https": 'http://154.236.162.34:1981'}
        session = requests.Session()
        for proxy in self.proxies:
        #Get a proxy from the pool
            try:
                symbol = 'amd'
                url = 'https://www.tipranks.com/stocks/'+symbol+'/stock-analysis'
                proxyy = random.choice(self.proxies)
                session.proxies = {"http": 'http://'+proxyy, "https": 'http://'+proxyy}
                session.get(url, timeout=1.5)
                #url = 'https://httpbin.org/ip'
                #response = requests.get(url,proxies={"http": 'http://'+proxy, "https": 'http://'+proxy})
                #response = requests.get(url,proxies={"https": 'http://'+proxy})
                #response = requests.get(url,proxies={"http": proxy, "https": proxy})
                #print(response.json())
                print(f'success with IP:{proxy}')
                break
            except:
                print("Skipping. Connnection error")
