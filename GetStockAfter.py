# 每日取得盤後股價

# 富邦新一代 API
# 參考網址："https://www.fbs.com.tw/TradeAPI/"

# 安裝方式-下載SDK，PIP指定路徑安裝
# pip install C:\fubon_neo-2.2.0-cp37-abi3-win_amd64.whl

import os
import json
from datetime import datetime
from types import SimpleNamespace
from fubon_neo.sdk import FubonSDK, Order
from fubon_neo.constant import TimeInForce, OrderType, PriceType, MarketType, BSAction

# 資料庫連線相關及Orm.Model
from db import dbinst, StockAfter
from sqlalchemy.sql import text

# from dotenv import get_key,load_dotenv

import StockLib as StockLib
from StockLib import getenv
from LineLib import PushMessageEarn2

# mail
from mail import SendGmail


from logger import WriteLogTxt


# def getStockAfter(stockList, strategy):
def getStockAfter():

    print("啟動時間 %s" % datetime.now())

    USER_ID = getenv("USER_ID")
    USER_PASSWORD = getenv("USER_PASSWORD")
    PFX_PATH = getenv("PFX_PATH")

    sdk = FubonSDK()
    accounts = sdk.login(USER_ID, USER_PASSWORD, PFX_PATH)
    sdk.init_realtime()  # 建立行情連線

    StockAfterDatas = []

    # to do休市時間
    # https://www.twse.com.tw/rwd/zh/holidaySchedule/holidaySchedule?date=20250000&response=html
    # checkOffDay

    # reststock = sdk.marketdata.rest_client.stock
    # res = reststock.historical.candles(**{'symbol': '2330', 'from': '2024-04-06', 'to': '2024-04-18'})
    # print(res)

    # reststock = sdk.marketdata.rest_client.stock
    # resp = reststock.historical.stats(symbol = "0050")

    # 股票行情快照（依市場別）
    # 市場別，可選 TSE 上市；OTC 上櫃；ESB 興櫃一般板；
    reststock = sdk.marketdata.rest_client.stock
    resp = reststock.snapshot.quotes(market="TSE")

    print("get StockAfter Detail")
    # TSE 上市
    # 取得時間
    stockdate = resp["date"]
    stockdate = stockdate[0:4] + stockdate[5:7] + stockdate[8:10]

    StockAfterDatas = resp["data"]
    # OTC 上櫃
    resp = reststock.snapshot.quotes(market="OTC")
    StockAfterDatas = StockAfterDatas + resp["data"]
    # ESB 興櫃
    resp = reststock.snapshot.quotes(market="ESB")
    StockAfterDatas = StockAfterDatas + resp["data"]

    try:
        with dbinst.getsession()() as session:
            # 取得該日期目前所有的盤後資料
            StockAfters = (
                session.query(StockAfter)
                .filter(StockAfter.stockdate == stockdate)
                .all()
            )
            # 將列表轉換成字典，加速查找 (O(1))
            stockcode_dict = {x.stockcode: x for x in StockAfters}

            iIdx = 0
            for data in StockAfterDatas:
                iIdx = iIdx + 1

                # 20250402 大量數據時，遍歷整個列表，查找會變慢。
                # 搜尋當日資料是否已經存在
                # item = next((x for x in StockAfters if x.stockcode == data['symbol']),None)

                # 直接查找，不用遍歷
                item = stockcode_dict.get(data["symbol"], None)

                # 如果不存在，則寫入資料
                if item == None:
                    article = StockAfter()
                    article.stockcode = data["symbol"]
                    article.stockdate = stockdate
                    article.openPrice = data["openPrice"] if "openPrice" in data else 0
                    article.highPrice = data["highPrice"] if "highPrice" in data else 0
                    article.lowPrice = data["lowPrice"] if "lowPrice" in data else 0
                    article.closePrice = (
                        data["closePrice"] if "closePrice" in data else 0
                    )
                    article.change = data["change"]
                    article.changePercent = data["changePercent"]
                    article.tradeVolume = data["tradeVolume"]
                    article.tradeValue = data["tradeValue"]
                    article.updatetime = StockLib.getNowDatetime()
                    session.add(article)

                    session.commit()
                    print(
                        f"{StockLib.getNowDatetime()}=[{iIdx}/{len(StockAfterDatas)}]({data["symbol"]}-{data["name"]})盤後資料取得完成"
                    )

                sss = "1"

    except Exception as e:
        print(f"Encounter exception: {e}")

    SendGmail(
        getenv("MAILTO"),
        "[C10 Stock]{0}=每日盤後股價更新取得完成".format(StockLib.getNowDatetime()),
        "完成時間：{0} \n分點總數：{1} \n完成數量：{2}".format(
            StockLib.getNowDatetime(), "", ""
        ),
    )
    print("結束時間 %s" % datetime.now())


# 直接執行這個模組，它會判斷為 true
# 從另一個模組匯入這個模組，它會判斷為 false
if __name__ == "__main__":

    getStockAfter()
