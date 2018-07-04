# -*- coding: utf-8 -*-
"""
Created on Fri Jun 22 20:50:41 2018

@author: M1400
"""

import requests
import pandas as pd
from bs4 import BeautifulSoup

url = 'https://www.investing.com/indices/ftse-malaysia-klci-components'
agent = {"User-Agent":'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}

def crawl(url = url, agent=agent):
    
    respond = requests.get(url,headers=agent)
    soup = BeautifulSoup(respond.text)
    index = soup.findAll('span',{'class':'arial_26 inlineblock pid-29078-last'})[0].text
    times = soup.findAll('span',{'class':'bold pid-29078-time'})[0].text
    top_30 = soup.select('tbody > tr > td')
    top_30_info=[top_30[i].text for i in range(855)]
    
    comp = [top_30_info[i] for i in range(5,296,10)]
    last = [top_30_info[i] for i in range(6,297,10)]
    high = [top_30_info[i] for i in range(7,298,10)]
    low = [top_30_info[i] for i in range(8,299,10)]
    chg = [top_30_info[i] for i in range(9,300,10)]
    chg_per = [top_30_info[i] for i in range(10,301,10)]
    vol = [top_30_info[i] for i in range(11,302,10)]
    
    df = pd.DataFrame()
    df['Name'] = comp
    df['Last'] = last
    df['High'] = high
    df['Low'] = low
    df['Change'] = chg
    df['Chg.%'] = chg_per
    df['Volume'] = vol
    
    pos = sum([float(i)>0 for i in chg])
    neg = sum([float(i)<0 for i in chg])
    neu = 30-pos-neg
    
    return [[index,times],df,[pos,neg,neu]]
    

    