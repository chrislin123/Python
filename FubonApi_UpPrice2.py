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
from db import dbinst,stockinfo,StockInfoType
from sqlalchemy.sql import text

# from dotenv import get_key,load_dotenv

import StockLib as StockLib
from StockLib import getenv
from LineLib import PushMessageEarn2

#mail
from mail import SendGmail


from logger import WriteLogTxt

# message = '{"isTest": true}'
# jmessage = json.loads(message)

# if jmessage['isTest'] == True:
#     try:
#         SendGmail(getenv("MAILTOSTORE"), '[股期漲停警示]{0}=成交價格{1}'.format("DataDate","2")  , "")
#         SendGmail(getenv("MAILTO"), '[股期漲停警示]{0}=成交價格{1}'.format("DataDate","2") , "")
#     except Exception as e:
#       print(f"Encounter exception: {e}")

#設定路徑及名稱
#log_obj = WriteLogTxt(r'D:\Project\Python','FubonAPI')
log_obj = WriteLogTxt(r'\FubonLog\FubonAPI2','FubonAPI')
log_obj.setup_logger()



#測試json轉python物件，轉換成功，但是無法判斷是否存在
#data = '{"event":"data","data":{"symbol":"2330","type":"EQUITY","exchange":"TWSE","market":"TSE","price":973,"size":1008,"bid":973,"ask":975,"volume":0,"isLimitUpPrice":true,"time":1743035482110891,"serial":11692},"id":"zjKnDEw2E2u64Y5R4Y1ZIvDZY7P5rYhlzmEgrVywt6x","channel":"trades"}'
# x = json.loads(data, object_hook=lambda d: SimpleNamespace(**d))
# print(x.event,x.data.symbol)


isLimitUpPriceList = []


#Sotck回傳訊息，資料處理
def handle_message(message):
    global isLimitUpPriceList
    log_obj.write_log_info(message)

    print(message)

    jmessage = json.loads(message)

    # if message['data']

    # if message['isTest'] == True:
    #     SendGmail(getenv("MAILTOSTORE"), '[股期漲停警示]{0}=成交價格{1}'.format("DataDate","2")
    #                 , "")

    # if '123' in jmessage:
    #     print('Y')
    # else:
    #     print('N')

    # isLimitUpPriceList.append('test')
    # print(len(isLimitUpPriceList))


    if jmessage["event"] == "data":
        respdata = jmessage["data"]
        if 'isLimitUpPrice' in respdata: #最後成交價為漲停價
            if 'isTrial' not in respdata: #非試搓
                if respdata["symbol"] not in isLimitUpPriceList: #不清單中才加入，且寄送通知
                    isLimitUpPriceList.append(respdata["symbol"])
                    #寄送漲停通知信
                    SendGmail(getenv("MAILTO"), '[C10 Stock]{0}=最後成交價為漲停價，時間：{1}'.format(respdata["symbol"],StockLib.getNowDatetime())
                        , '')


#連線狀態
def handle_connect():
    print('market data connected')

#斷線重連
def handle_disconnect(code, message):
    print(f'market data disconnect: {code}, {message}')
    stock.connect()
    print("Reconnected Succuess")
    print("Resubscribe")
    stock.subscribe({
        # 重新訂閱您已訂閱過的Channel與Symbol
        'channel': 'trades',
        'symbols': mySymbols
    })



USER_ID= getenv('USER_ID')
USER_PASSWORD = getenv('USER_PASSWORD')
PFX_PATH = getenv('PFX_PATH')

sdk = FubonSDK()
accounts = sdk.login(USER_ID,USER_PASSWORD,PFX_PATH)
sdk.init_realtime()  # 建立行情連線


# stock = sdk.marketdata.websocket_client.stock
# stock.on('message', handle_message)
# stock.connect()
# stock.subscribe({
#     'channel': 'indices',
#     'symbol': 'IR0001'
# })


mySymbols = []
try:
    with dbinst.getsession()() as session:

        sinfotype = "StockFutures"
        remark = "2"

        articles = session.query(StockInfoType).filter(StockInfoType.infotype == sinfotype  ,StockInfoType.remark == remark).all()

        for data in articles:
            mySymbols.append(data.stockcode)

except Exception as e:
    print(f"Encounter exception: {e}")



# #可以考慮用切換的方式處理訂閱
# mySymbols1 = mySymbols[:200]
# mySymbols2 = mySymbols[200:]

# #取得即時報價Socket(symbols:最多兩百個)
# stock = sdk.marketdata.websocket_client.stock
# stock.on('message', handle_message)
# stock.on("connect", handle_connect)
# stock.on("disconnect", handle_disconnect)
# stock.connect()
# stock.subscribe({
#     'channel': 'trades',
#     'symbols': mySymbols1
# })

# mySymbols1 = []
# mySymbols1.append('2330')
# # mySymbols1.append('3481')
# mySymbols1.append('2468')


#取得即時報價Socket(symbols:最多兩百個)
stock = sdk.marketdata.websocket_client.stock
stock.on('message', handle_message)
stock.on("connect", handle_connect)
stock.on("disconnect", handle_disconnect)
stock.connect()
stock.subscribe({
    'channel': 'trades',
    'symbols': mySymbols
})





#股票或指數列表（依條件查詢）
# reststock = sdk.marketdata.rest_client.stock
# resp =  reststock.intraday.tickers(type='INDEX', exchange="TWSE")
# resp =  reststock.intraday.tickers(type='INDEX', exchange="TWSE", isNormal=True)
# resp =  reststock.intraday.tickers(type='EQUITY', exchange="TWSE", isNormal=True)
# resp =  reststock.intraday.tickers(type='INDEX', exchange="TPEx")

#取得單筆資料
# reststock = sdk.marketdata.rest_client.stock
# resp = reststock.intraday.quote(symbol='2330')
# print(resp)

mySymbols1 = []
#PushMessageEarn2(resp["symbol"])



# sdk.init_realtime() # 建立行情連線
# reststock = sdk.marketdata.rest_client.stock
# resp = reststock.intraday.ticker(symbol='2330')
# print(resp)







































