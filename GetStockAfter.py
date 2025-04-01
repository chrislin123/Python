#富邦新一代 API
#參考網址："https://www.fbs.com.tw/TradeAPI/"

#安裝方式-下載SDK，PIP指定路徑安裝
#pip install C:\fubon_neo-2.2.0-cp37-abi3-win_amd64.whl

import os
import json
from types import SimpleNamespace
from fubon_neo.sdk import FubonSDK, Order
from fubon_neo.constant import TimeInForce, OrderType,PriceType,MarketType,BSAction
#資料庫連線相關及Orm.Model
from db import dbinst,StockAfter
from sqlalchemy.sql import text

# from dotenv import get_key,load_dotenv

import StockLib as StockLib
from StockLib import getenv
from LineLib import PushMessageEarn2

#mail
from mail import SendGmail


from logger import WriteLogTxt


USER_ID= getenv('USER_ID')
USER_PASSWORD = getenv('USER_PASSWORD')
PFX_PATH = getenv('PFX_PATH')

sdk = FubonSDK()
accounts = sdk.login(USER_ID,USER_PASSWORD,PFX_PATH)
sdk.init_realtime()  # 建立行情連線


StockAfterDatas = []

#股票行情快照（依市場別）
#市場別，可選 TSE 上市；OTC 上櫃；ESB 興櫃一般板；
reststock = sdk.marketdata.rest_client.stock
resp = reststock.snapshot.quotes(market='TSE')

#TSE 上市
#取得時間
stockdate = resp['date']
stockdate = stockdate[0:4]+stockdate[5:7]+stockdate[8:10]

StockAfterDatas= resp['data']
#OTC 上櫃
resp = reststock.snapshot.quotes(market='OTC')
StockAfterDatas = StockAfterDatas + resp['data']
#ESB 興櫃
resp = reststock.snapshot.quotes(market='ESB')
StockAfterDatas = StockAfterDatas + resp['data']


try:
    with dbinst.getsession()() as session:
        #取得該日期目前所有的盤後資料
        StockAfters = session.query(StockAfter).filter(StockAfter.stockdate == stockdate).all()

        iIdx = 0
        for data in StockAfterDatas:
            iIdx = iIdx + 1
            #搜尋當日資料是否已經存在
            item = next((x for x in StockAfters if x.stockcode == data['symbol']),None)

            #如果不存在，則寫入資料
            if item == None:
                article = StockAfter()
                article.stockcode = data['symbol']
                article.stockdate = stockdate
                article.openPrice = data['openPrice'] if 'openPrice' in data else 0
                article.highPrice = data['highPrice'] if 'highPrice' in data else 0
                article.lowPrice = data['lowPrice'] if 'lowPrice' in data else 0
                article.closePrice = data['closePrice'] if 'closePrice' in data else 0
                article.change = data['change']
                article.changePercent = data['changePercent']
                article.tradeVolume = data['tradeVolume']
                article.tradeValue = data['tradeValue']
                article.updatetime = StockLib.getNowDatetime()
                session.add(article)

                session.commit()
                print('[{2}/{3}]({0}-{1})寫入'.format(data['symbol'],data['name'],iIdx,len(StockAfterDatas)))

            sss = '1'


except Exception as e:
    print(f"Encounter exception: {e}")
