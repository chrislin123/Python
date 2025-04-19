#富邦新一代 API
#參考網址："https://www.fbs.com.tw/TradeAPI/"

#安裝方式-下載SDK，PIP指定路徑安裝
#pip install C:\fubon_neo-2.2.0-cp37-abi3-win_amd64.whl

import os
import json
import datetime
from types import SimpleNamespace
from fubon_neo.sdk import FubonSDK, Order
from fubon_neo.constant import TimeInForce, OrderType,PriceType,MarketType,BSAction
#資料庫連線相關及Orm.Model
from db import dbinst,stockinfo,StockInfoType,StockLog
from sqlalchemy.sql import text
import asyncio
import threading
# from dotenv import get_key,load_dotenv

import StockLib as StockLib
from StockLib import getenv
from LineLib import PushMessageEarn2

#mail
from mail import SendGmail


from logger import WriteLogTxt


# loop = asyncio.get_event_loop()

def start_background_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()

background_loop = asyncio.new_event_loop()
threading.Thread(target=start_background_loop, args=(background_loop,), daemon=True).start()


async def insMaxVol2330(data):
    try:
        async with dbinst.get_asyncsession()() as session:
            PriceType = ''
            if data['price'] == data['bid']:
                PriceType = 'bid'
            if data['price'] == data['ask']:
                PriceType = 'ask'
            Stocklog = StockLog()
            Stocklog.logtype = 'TestASync'
            Stocklog.logdate = PriceType
            Stocklog.key1 = data["symbol"]
            Stocklog.key2 = data['size']
            Stocklog.logstatus = 'true'
            Stocklog.memo = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
            Stocklog.logdatetime = StockLib.getNowDatetime()
            session.add(Stocklog)
            await session.commit()

    except Exception as e:
        print(f"[❌ async db error] {e}")



isLimitUpPriceList = []


#Sotck回傳訊息，資料處理
def handle_message(message):
    global isLimitUpPriceList
    # log_obj.write_log_info(message)

    print(message)

    jmessage = json.loads(message)

    if jmessage["event"] == "data":
        respdata = jmessage["data"]

        if 'isTrial' not in respdata: #非試搓

            if 'size' in respdata: #成交單量
                if respdata["size"] > 0:
                    sss=''
                    #非同步寫入資料庫
                    # 將 async 任務註冊到背景 loop
                    #loop.create_task(insMaxVol2330(respdata))
                    #asyncio.get_event_loop().create_task(insMaxVol2330(respdata))
                    #asyncio.create_task(insMaxVol2330(respdata))
                    #寄送大單通知信
                    # SendGmail(getenv("MAILTO"), '[C10 Stock](特大單){0}=時間：{1}，數量：{2}'.format(respdata["symbol"],StockLib.getNowDatetime(),respdata["size"])
                    #     , '')

    if jmessage["event"] == "pong":
        respdata = jmessage["data"]

        if 'time' in respdata: #成交單量
            if respdata["time"] > 100:

                background_loop.call_soon_threadsafe(asyncio.create_task, insMaxVol2330(respdata))
                # asyncio.get_event_loop().create_task(insMaxVol2330(respdata))
                #asyncio.create_task(insMaxVol2330(respdata))

                #寄送特大單通知信
                # SendGmail(getenv("MAILTO"), '[C10 Stock](特大單){0}=時間：{1}，數量：{2}'.format('2330',StockLib.getNowDatetime(),respdata["time"])
                #     , '')


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

mySymbols = []
mySymbols.append('2330')


USER_ID= getenv('USER_ID')
USER_PASSWORD = getenv('USER_PASSWORD')
PFX_PATH = getenv('PFX_PATH')

sdk = FubonSDK()
accounts = sdk.login(USER_ID,USER_PASSWORD,PFX_PATH)
sdk.init_realtime()  # 建立行情連線

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

print("🟢 WebSocket running...")

# # 啟動背景 loop（確保主線程不退出）
# try:
#     print("背景事件迴圈啟動中...")
#     loop.run_forever()
# except KeyboardInterrupt:
#     print("事件迴圈結束")
# finally:
#     loop.close()


































