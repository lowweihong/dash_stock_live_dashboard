import requests
import pandas as pd
from bs4 import BeautifulSoup
from lxml.html.soupparser import fromstring
url = 'https://www.investing.com/indices/ftse-malaysia-klci-components'
agent = {"User-Agent": 'Mozilla/5.0 (Windows NT 6.3; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/59.0.3071.115 Safari/537.36'}


def crawl(url=url, agent=agent):
    respond = requests.get(url, headers=agent)
    soup = BeautifulSoup(respond.text)
    index = soup.findAll('span', {'class': 'arial_26 inlineblock pid-29078-last'})[0].text
    times = soup.findAll('span', {'class': 'bold pid-29078-time'})[0].text
    top_30 = soup.select('table#cr1 > tbody > tr')
    comp = [] ; last = [] ; high=[] ; low =[] ; chg=[]; chg_per=[]; vol=[]

    for ele in top_30:
        temp = [i.text for i in ele.find_all('td')]
        comp.append(temp[1])
        last.append(temp[2])
        high.append(temp[3])
        low.append(temp[4])
        chg.append(temp[5])
        chg_per.append(temp[6])
        vol.append(temp[7])

    df = pd.DataFrame()
    df['Name'] = comp
    df['Last'] = last
    df['High'] = high
    df['Low'] = low
    df['Change'] = chg
    df['Chg.%'] = chg_per
    df['Volume'] = vol

    pos = sum([float(i) > 0 for i in chg])
    neg = sum([float(i) < 0 for i in chg])
    neu = 30 - pos - neg

    return [[index, times], df, [pos, neg, neu]]

crawl()
