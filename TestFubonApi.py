#富邦新一代 API
#參考網址："https://www.fbs.com.tw/TradeAPI/"

import json
from fubon_neo.sdk import FubonSDK, Order
from fubon_neo.constant import TimeInForce, OrderType,PriceType,MarketType,BSAction
#資料庫連線相關及Orm.Model
from db import dbinst,stockinfo,StockInfoType
from sqlalchemy.sql import text

# from dotenv import get_key,load_dotenv
# import os
from StockLib import getenv
from LineLib import PushMessageEarn2

#mail
from mail import SendGmail


# message = '{"isTest": true}'
# jmessage = json.loads(message)

# if jmessage['isTest'] == True:
#     try:
#         SendGmail(getenv("MAILTOSTORE"), '[股期漲停警示]{0}=成交價格{1}'.format("DataDate","2")  , "")
#         SendGmail(getenv("MAILTO"), '[股期漲停警示]{0}=成交價格{1}'.format("DataDate","2") , "")
#     except Exception as e:
#       print(f"Encounter exception: {e}")


#Sotck回傳訊息，資料處理
def handle_message(message):
    print(message)

    jmessage = json.loads(message)

    # if message['data']

    # if message['isTest'] == True:
    #     SendGmail(getenv("MAILTOSTORE"), '[股期漲停警示]{0}=成交價格{1}'.format("DataDate","2")
    #                 , "")

    if '123' in jmessage:
        print('Y')
    else:
        print('N')
    # print(jmessage.has_key('123'))

    if jmessage["event"] == "data":
        respdata = jmessage["data"]
        if 'isLimitUpPrice' in respdata:
            print("{0} is {1} 漲停".format(respdata["symbol"],respdata["isLimitUpPrice"]))




    # if jmessage["event"] == "pong":
    #     print("event is {0}".format(jmessage["event"]))

#連線狀態
def handle_connect():
    print('market data connected')

#斷線重連
def handle_disconnect(code, message):
    print(f'market data disconnect: {code}, {message}')
    stock.connect()
    print("Reconnected Succuess")
    print("Resubscribe")
    stock.subscribe({    # 重新訂閱您已訂閱過的Channel與Symbol
        'channel': '<CHANNEL_NAME>',
        'symbol': '<SYMBOL_ID>'
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


# mySymbols = []
# try:
#     with dbinst.getsession()() as session:

#         sinfotype = "StockFutures"

#         articles = session.query(StockInfoType).filter(StockInfoType.infotype == sinfotype).all()

#         for data in articles:
#             mySymbols.append(data.stockcode)

# except Exception as e:
#     print(f"Encounter exception: {e}")



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

mySymbols1 = []
mySymbols1.append('2330')
# mySymbols1.append('3481')
mySymbols1.append('2468')
mySymbols1.append('4541')
mySymbols1.append('6140')

#取得即時報價Socket(symbols:最多兩百個)
stock = sdk.marketdata.websocket_client.stock
stock.on('message', handle_message)
stock.on("connect", handle_connect)
stock.on("disconnect", handle_disconnect)
stock.connect()
stock.subscribe({
    'channel': 'trades',
    'symbols': mySymbols1
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







































