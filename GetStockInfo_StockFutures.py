###取得股票期貨清單
###來源：台灣期交所
###網址：https://www.taifex.com.tw/file/taifex/CHINESE/2/2_stockinfo.ods

import os
import requests
from datetime import datetime
from bs4 import BeautifulSoup
import pandas as pd

#資料庫連線相關及Orm.Model
from db import dbinst,stockinfo,StockInfoType
from sqlalchemy.sql import text

#股票期貨清單
stockinfo_URL = 'https://www.taifex.com.tw/file/taifex/CHINESE/2/2_stockinfo.ods'

#由網址讀取.ods檔案到pandas分析，鎖定第二個欄位，忽略前兩行
df = pd.read_excel(stockinfo_URL, engine='odf', usecols=[ 2], skiprows=2)

try:

    with dbinst.getsession()() as session:

        sinfotype = "StockFutures"

        #設定為尚未轉檔
        params =  { "updstatus": "N","infotype": sinfotype}
        sql = text(" update StockInfoType set  updstatus = :updstatus where infotype = :infotype ")
        session.execute(sql,params)
        session.commit()


        for data in df.values:
            print(data[0])
            now = datetime.now()
            date_time = now.strftime("%Y-%m-%dT%H:%M:%S")
            print("date and time:",date_time)

            article = session.query(StockInfoType).filter(StockInfoType.stockcode == str(data[0])).first()
            if article == None:
                article = StockInfoType()
                article.stockcode = str(data[0])
                article.infotype = sinfotype
                article.updatetime = date_time
                article.status = "Y"
                article.updstatus = "Y"
                session.add(article)

            else:
                article.updatetime = date_time
                article.updstatus = "Y"

            session.commit()


        #如果本日沒有更新代表個股停用或是下市，則狀態改為N
        params =  { "updstatus": "N" ,"status": "N"}
        sql = text(" update StockInfoType set status = :status where updstatus = :updstatus ")
        session.execute(sql,params)
        session.commit()


except Exception as e:
    print(f"Encounter exception: {e}")












#上市股票清單
tses = []
#ETF清單
etfs = []
#上櫃股票清單
otcs = []
#興櫃股票清單
otc2s = []

datatype = ""


res = requests.get(TWSE_URL)
soup = BeautifulSoup(res.text, "lxml")
tr = soup.findAll('tr')
for raw in tr:
     data = [td.get_text() for td in raw.findAll("td")]
     #判斷清單類別
     if len(data) == 1:
         print(data[0])
         if data[0].strip() == "股票":
             datatype = "上市"
         elif data[0].strip() == "ETF":
             datatype = "etf"


     #資料分析彙整
     if len(data) == 7:
        rowData = []

        if '\u3000' in data[0]:
           code, name = data[0].split('\u3000')
           rowData = [code, name , data[4]]
        else:
           rowData = ["","", data[4]]

        if datatype == "上市":
            rowData.append("tse")
            tses.append(rowData)
        elif datatype == "etf":
            rowData.append("etf")
            etfs.append(rowData)

#上櫃
res = requests.get(TPEX_URL)
soup = BeautifulSoup(res.text, "lxml")
tr = soup.findAll('tr')
for raw in tr:
     data = [td.get_text() for td in raw.findAll("td")]
     #判斷清單類別
    #  if len(data) == 1:
    #      print(data[0])
    #      if data[0].strip() == "股票":
    #          datatype = "上市"
    #      elif data[0].strip() == "ETF":
    #          datatype = "etf"


     #資料分析彙整
     if len(data) == 7:
        rowData = []

        if '\u3000' in data[0]:
           code, name = data[0].split('\u3000')
           rowData = [code, name , data[4]]
        else:
           rowData = ["","", data[4]]

        rowData.append("otc")
        otcs.append(rowData)
        # if datatype == "上市":
        #     rowData.append("tse")
        #     tses.append(rowData)
        # elif datatype == "etf":
        #     rowData.append("etf")
        #     etfs.append(rowData)

#興櫃
res = requests.get(TPEX2_URL)
soup = BeautifulSoup(res.text, "lxml")
tr = soup.findAll('tr')
for raw in tr:
     data = [td.get_text() for td in raw.findAll("td")]
     #判斷清單類別
    #  if len(data) == 1:
    #      print(data[0])
    #      if data[0].strip() == "股票":
    #          datatype = "上市"
    #      elif data[0].strip() == "ETF":
    #          datatype = "etf"


     #資料分析彙整
     if len(data) == 7:
        rowData = []

        if '\u3000' in data[0]:
           code, name = data[0].split('\u3000')
           rowData = [code, name , data[4]]
        else:
           rowData = ["","", data[4]]

        rowData.append("otc2")
        otc2s.append(rowData)
        # if datatype == "上市":
        #     rowData.append("tse")
        #     tses.append(rowData)
        # elif datatype == "etf":
        #     rowData.append("etf")
        #     etfs.append(rowData)

#寫入資料庫


try:

    with dbinst.getsession()() as session:



        #設定為尚未轉檔
        params =  { "updstatus": "N"}
        sql = text(" update stockinfo set  updstatus = :updstatus ")
        session.execute(sql,params)
        session.commit()

        #新增更新-tses
        for row in tses:

            #排除非股票
            if row[2] == "":
                continue
            print(row)
            now = datetime.now()
            date_time = now.strftime("%Y-%m-%dT%H:%M:%S")
            print("date and time:",date_time)

            article = session.query(stockinfo).filter(stockinfo.stockcode == row[0]).first()
            if article == None:
                article = stockinfo()
                article.stockcode = row[0]
                article.stockname = row[1]
                article.type = row[3]
                article.industry = row[2]
                article.updatetime = date_time
                article.status = "Y"
                article.updstatus = "Y"
                session.add(article)

            else:
                article.stockname = row[1]
                article.updatetime = date_time
                article.updstatus = "Y"

            session.commit()

        #新增更新-etfs
        for row in etfs:


            print(row)
            now = datetime.now()
            date_time = now.strftime("%Y-%m-%dT%H:%M:%S")
            print("date and time:",date_time)

            article = session.query(stockinfo).filter(stockinfo.stockcode == row[0]).first()
            if article == None:
                article = stockinfo()
                article.stockcode = row[0]
                article.stockname = row[1]
                article.type = row[3]
                article.industry = row[2]
                article.updatetime = date_time
                article.status = "Y"
                article.updstatus = "Y"
                session.add(article)

            else:
                article.stockname = row[1]
                article.updatetime = date_time
                article.updstatus = "Y"

            session.commit()

        #新增更新-otcs
        for row in otcs:
            #排除非股票
            if row[2] == "":
                continue

            print(row)
            now = datetime.now()
            date_time = now.strftime("%Y-%m-%dT%H:%M:%S")
            print("date and time:",date_time)

            article = session.query(stockinfo).filter(stockinfo.stockcode == row[0]).first()
            if article == None:
                article = stockinfo()
                article.stockcode = row[0]
                article.stockname = row[1]
                article.type = row[3]
                article.industry = row[2]
                article.updatetime = date_time
                article.status = "Y"
                article.updstatus = "Y"
                session.add(article)

            else:
                article.stockname = row[1]
                article.updatetime = date_time
                article.updstatus = "Y"

            session.commit()

        #新增更新-otc2s
        for row in otc2s:
            #排除非股票
            if row[2] == "":
                continue

            print(row)
            now = datetime.now()
            date_time = now.strftime("%Y-%m-%dT%H:%M:%S")
            print("date and time:",date_time)

            article = session.query(stockinfo).filter(stockinfo.stockcode == row[0]).first()
            if article == None:
                article = stockinfo()
                article.stockcode = row[0]
                article.stockname = row[1]
                article.type = row[3]
                article.industry = row[2]
                article.updatetime = date_time
                article.status = "Y"
                article.updstatus = "Y"
                session.add(article)

            else:
                article.stockname = row[1]
                article.updatetime = date_time
                article.updstatus = "Y"

            session.commit()

        #如果本日沒有更新代表個股停用或是下市，則狀態改為N
        params =  { "updstatus": "N" ,"status": "N"}
        sql = text(" update stockinfo set status = :status where updstatus = :updstatus ")
        session.execute(sql,params)
        session.commit()


except Exception as e:
    print(f"Encounter exception: {e}")
# finally:
#     # 斷開資料庫的連線
#     mssql_engine.dispose()







ss = ''



#結束程式
# exit()





