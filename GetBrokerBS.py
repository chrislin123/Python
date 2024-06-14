import os
import re
import time
import random
import requests
from datetime import datetime
from bs4 import BeautifulSoup
import pandas as pd

#資料庫相關
# import pymssql
from collections import deque


#資料庫連線相關及Orm.Model
from db import dbinst,StockBroker1,StockBrokerBS



# 官方來源如下：
# 上櫃每日
# https://www.tpex.org.tw/web/stock/aftertrading/broker_trading/brokerBS.php?l=zh-tw
# 上市每日
# https://bsr.twse.com.tw/bshtm/

# 各大券商皆有統計，來源可能為同一廠商系統：

# http://just2.entrust.com.tw/Z/ZG/ZGB/ZGB.djhtm
# https://fubon-ebrokerdj.fbs.com.tw/Z/ZG/ZGB/ZGB.djhtm
# https://www.esunsec.com.tw/tw-rank/z/ZG/ZGB/ZGB.djhtm
# http://newjust.masterlink.com.tw/z/zg/zgb/zgb0.djhtm



#print(res.text)
# print(res.text.partition('\n')[0])
# soup = BeautifulSoup(res.text, "lxml")

StockBroker1s=[]
try:
    with dbinst.getsession()() as session:
        StockBroker1s = session.query(StockBroker1).filter(StockBroker1.brokerparentyn == 'N').all()

except Exception as e:
    print(f"Encounter exception: {e}")



idx = 0
for StockBrokerData in StockBroker1s:
    idx += 1

    #測試出問題的序號，可移除
    # if idx != 37:
    #     continue

    #排除已經沒有使用的券商分點資料，避免解析出問題
    if "停" in StockBrokerData.brokername:
        continue

    print("{0}/{1}--[{2}]{3}".format(idx,len(StockBroker1s),StockBrokerData.brokercode,StockBrokerData.brokername))

    randint = random.randint(5,10)
    #間隔三秒
    print('間隔{0}秒'.format(randint))
    time.sleep(randint)



    TWSE_URL= 'https://newjust.masterlink.com.tw/z/zg/zgb/zgb0.djhtm?a={0}&b={1}&c=E&d=1'
    TWSE_URL = TWSE_URL.format(StockBrokerData.brokerparentcode,StockBrokerData.brokercode)
    header = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
    }

    res = requests.get(TWSE_URL, headers=header)
    soup = BeautifulSoup(res.text, "lxml")
    tables = soup.findAll('table')

    #分點代碼
    brokercode = StockBrokerData.brokercode
    #取得資料日期
    DataDate = ""

    allbuys = []
    allsells = []
    for table in tables:

        #排除不需要的Table
        if "分點明細查詢" in table.text:
            if table.findAll('div'):
                Dates = re.split('：', table.findAll('div')[0].text)
                DataDate = Dates[2]
            continue


        #判斷Table是否包含"買超""賣超"才進行資料分析
        if "買超" in table.text:


            for tr in table.findAll('tr'):
                #排除不需要的TR
                if "買超" in tr.text :
                    continue
                if "券商名稱" in tr.text :
                    continue
                if "無此券商分點交易資料" in tr.findAll("td")[0].text:
                    continue

                stockcode = ""
                stockname = ""
                stockbuy = ""
                stocksell = ""
                stockdiff = ""


                #有些連結直接使用<A href>
                #有些連結使用Javescript產生，所以變成要解析<script>中的內容取得資料
                if tr.findAll("a"):
                    data = tr.findAll("a")[0].text
                    #判斷前六個字串是否是數字，否則只取前五個
                    if str(data[0:6]).encode().isalnum():
                        stockcode = data[0:6]
                        stockname = data[6:]
                    else:
                        stockcode = data[0:5]
                        stockname = data[5:]
                    sa =""
                else:
                    datas = re.split("'",tr.findAll("td")[0].contents[1].text)
                    stockcode = datas[1].replace("AS","")
                    stockname = datas[3]


                data = [td.get_text() for td in tr.findAll("td")]
                stockbuy = data[1].replace(",","")
                stocksell = data[2].replace(",","")
                stockdiff = data[3].replace(",","")

                allbuys.append([stockcode,stockname,stockbuy,stocksell,stockdiff])

                s1= 0



            s1= 0

        elif "賣超" in table.text:
            for tr in table.findAll('tr'):
                #排除不需要的TR
                if "賣超" in tr.text :
                    continue
                if "券商名稱" in tr.text :
                    continue
                if "無此券商分點交易資料" in tr.findAll("td")[0].text:
                    continue

                stockcode = ""
                stockname = ""
                stockbuy = ""
                stocksell = ""
                stockdiff = ""


                #有些連結直接使用<A href>
                #有些連結使用Javescript產生，所以變成要解析<script>中的內容取得資料
                if tr.findAll("a"):
                    data = tr.findAll("a")[0].text
                    #判斷前六個字串是否是數字，否則只取前五個
                    if str(data[0:6]).encode().isalnum():
                        stockcode = data[0:6]
                        stockname = data[6:]
                    else:
                        stockcode = data[0:5]
                        stockname = data[5:]
                    sa =""
                else:
                    datas = re.split("'",tr.findAll("td")[0].contents[1].text)
                    stockcode = datas[1].replace("AS","")
                    stockname = datas[3]


                data = [td.get_text() for td in tr.findAll("td")]
                stockbuy = data[1].replace(",","")
                stocksell = data[2].replace(",","")
                stockdiff = data[3].replace(",","")


                allsells.append([stockcode,stockname,stockbuy,stocksell,stockdiff])

                s1= 0

            s1= 0




    #寫入資料庫
    try:

        with dbinst.getsession()() as session:


            #買超
            for data in allbuys:
                print(data)
                date_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

                article = session.query(StockBrokerBS).filter(
                        StockBrokerBS.brokercode == brokercode
                        ,StockBrokerBS.stockdate == DataDate
                        ,StockBrokerBS.stockcode == data[0]
                        ).first()

                if article == None:
                    article = StockBrokerBS()
                    article.brokercode = brokercode
                    article.stockcode = data[0]
                    article.stockdate = DataDate
                    article.isbuyover = 'Y'
                    article.buyvol = data[2]
                    article.sellvol = data[3]
                    article.diffvol = data[4]
                    article.updatetime = date_time
                    session.add(article)
                else:
                    article.brokercode = brokercode
                    article.stockcode = data[0]
                    article.stockdate = DataDate
                    article.isbuyover = 'Y'
                    article.buyvol = data[2]
                    article.sellvol = data[3]
                    article.diffvol = data[4]
                    article.updatetime = date_time

                session.commit()

            #賣超
            for data in allsells:
                print(data)
                date_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

                article = session.query(StockBrokerBS).filter(
                        StockBrokerBS.brokercode == brokercode
                        ,StockBrokerBS.stockdate == DataDate
                        ,StockBrokerBS.stockcode == data[0]
                        ).first()

                if article == None:
                    article = StockBrokerBS()
                    article.brokercode = brokercode
                    article.stockcode = data[0]
                    article.stockdate = DataDate
                    article.isbuyover = 'N'
                    article.buyvol = data[2]
                    article.sellvol = data[3]
                    article.diffvol = data[4]
                    article.updatetime = date_time
                    session.add(article)
                else:
                    article.brokercode = brokercode
                    article.stockcode = data[0]
                    article.stockdate = DataDate
                    article.isbuyover = 'N'
                    article.buyvol = data[2]
                    article.sellvol = data[3]
                    article.diffvol = data[4]
                    article.updatetime = date_time

                session.commit()

    except Exception as e:
        print(f"Encounter exception: {e}")



s=''














