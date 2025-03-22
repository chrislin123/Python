#富邦新一代 API
#參考網址："https://www.fbs.com.tw/TradeAPI/"


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

#顯示訊息
def handle_message(message):
    print(message)
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



#股票或指數列表（依條件查詢）
reststock = sdk.marketdata.rest_client.stock
# resp =  reststock.intraday.tickers(type='INDEX', exchange="TWSE")
# resp =  reststock.intraday.tickers(type='INDEX', exchange="TWSE", isNormal=True)
# resp =  reststock.intraday.tickers(type='EQUITY', exchange="TWSE", isNormal=True)
# resp =  reststock.intraday.tickers(type='INDEX', exchange="TPEx")

#取得單筆資料
reststock = sdk.marketdata.rest_client.stock
resp = reststock.intraday.quote(symbol='2330')
print(resp)


# PushMessageEarn2(resp["date"])



# sdk.init_realtime() # 建立行情連線
# reststock = sdk.marketdata.rest_client.stock
# resp = reststock.intraday.ticker(symbol='2330')
# print(resp)



mySymbols = []
try:
    with dbinst.getsession()() as session:

        sinfotype = "StockFutures"

        articles = session.query(StockInfoType).filter(StockInfoType.infotype == sinfotype).all()

        for data in articles:
            mySymbols.append(data.stockcode)

except Exception as e:
    print(f"Encounter exception: {e}")



#可以考慮用切換的方式處理訂閱
mySymbols1 = mySymbols[:200]
mySymbols2 = mySymbols[200:]

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



































