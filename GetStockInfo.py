# 股票基本資料轉檔

import os
import requests
from datetime import datetime
from bs4 import BeautifulSoup
import pandas as pd

# 資料庫連線相關及Orm.Model
from db import dbinst, stockinfo
from sqlalchemy.sql import text


# 上市
TWSE_URL = "https://isin.twse.com.tw/isin/C_public.jsp?strMode=2"
# 上櫃
TPEX_URL = "https://isin.twse.com.tw/isin/C_public.jsp?strMode=4"
# 興櫃
TPEX2_URL = "https://isin.twse.com.tw/isin/C_public.jsp?strMode=5"


# 上市股票清單
tses = []
# ETF清單
etfs = []
# 上櫃股票清單
otcs = []
# 興櫃股票清單
otc2s = []

datatype = ""


def getStockInfo():

    res = requests.get(TWSE_URL)
    soup = BeautifulSoup(res.text, "lxml")
    tr = soup.findAll("tr")
    for raw in tr:
        data = [td.get_text() for td in raw.findAll("td")]
        # 判斷清單類別
        if len(data) == 1:
            print(data[0])
            if data[0].strip() == "股票":
                datatype = "上市"
            elif data[0].strip() == "ETF":
                datatype = "etf"

        # 資料分析彙整
        if len(data) == 7:
            rowData = []

            if "\u3000" in data[0]:
                code, name = data[0].split("\u3000")
                rowData = [code, name, data[4]]
            else:
                rowData = ["", "", data[4]]

            if datatype == "上市":
                rowData.append("tse")
                tses.append(rowData)
            elif datatype == "etf":
                rowData.append("etf")
                etfs.append(rowData)

    # 上櫃
    res = requests.get(TPEX_URL)
    soup = BeautifulSoup(res.text, "lxml")
    tr = soup.findAll("tr")
    for raw in tr:
        data = [td.get_text() for td in raw.findAll("td")]

        # 資料分析彙整
        if len(data) == 7:
            rowData = []

            if "\u3000" in data[0]:
                code, name = data[0].split("\u3000")
                rowData = [code, name, data[4]]
            else:
                rowData = ["", "", data[4]]

            rowData.append("otc")
            otcs.append(rowData)

    # 興櫃
    res = requests.get(TPEX2_URL)
    soup = BeautifulSoup(res.text, "lxml")
    tr = soup.findAll("tr")
    for raw in tr:
        data = [td.get_text() for td in raw.findAll("td")]

        # 資料分析彙整
        if len(data) == 7:
            rowData = []

            if "\u3000" in data[0]:
                code, name = data[0].split("\u3000")
                rowData = [code, name, data[4]]
            else:
                rowData = ["", "", data[4]]

            rowData.append("otc2")
            otc2s.append(rowData)

    # 寫入資料庫
    try:

        with dbinst.getsession()() as session:

            # 設定為尚未轉檔
            params = {"updstatus": "N"}
            sql = text(" update stockinfo set  updstatus = :updstatus ")
            session.execute(sql, params)
            session.commit()

            # 新增更新-tses
            for row in tses:

                # 排除非股票
                if row[2] == "":
                    continue
                print(row)
                now = datetime.now()
                date_time = now.strftime("%Y-%m-%dT%H:%M:%S")
                print("date and time:", date_time)

                article = (
                    session.query(stockinfo)
                    .filter(stockinfo.stockcode == row[0])
                    .first()
                )
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

            # 新增更新-etfs
            for row in etfs:

                print(row)
                now = datetime.now()
                date_time = now.strftime("%Y-%m-%dT%H:%M:%S")
                print("date and time:", date_time)

                article = (
                    session.query(stockinfo)
                    .filter(stockinfo.stockcode == row[0])
                    .first()
                )
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

            # 新增更新-otcs
            for row in otcs:
                # 排除非股票
                if row[2] == "":
                    continue

                print(row)
                now = datetime.now()
                date_time = now.strftime("%Y-%m-%dT%H:%M:%S")
                print("date and time:", date_time)

                article = (
                    session.query(stockinfo)
                    .filter(stockinfo.stockcode == row[0])
                    .first()
                )
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

            # 新增更新-otc2s
            for row in otc2s:
                # 排除非股票
                if row[2] == "":
                    continue

                print(row)
                now = datetime.now()
                date_time = now.strftime("%Y-%m-%dT%H:%M:%S")
                print("date and time:", date_time)

                article = (
                    session.query(stockinfo)
                    .filter(stockinfo.stockcode == row[0])
                    .first()
                )
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

            # 如果本日沒有更新代表個股停用或是下市，則狀態改為N
            params = {"updstatus": "N", "status": "N"}
            sql = text(
                " update stockinfo set status = :status where updstatus = :updstatus "
            )
            session.execute(sql, params)
            session.commit()

    except Exception as e:
        print(f"Encounter exception: {e}")


# 直接執行這個模組，它會判斷為 true
# 從另一個模組匯入這個模組，它會判斷為 false
if __name__ == "__main__":

    getStockInfo()
