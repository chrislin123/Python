
import os
from datetime import datetime
import requests
import pandas as pd

#讀取機敏設定檔
from dotenv import get_key,load_dotenv

def getenv(getenv):
    load_dotenv()
    return os.getenv(getenv)

def LogRunTimeToCsv(self , FileFullName):

    # os.path.basename(FileFullName).split('.')[0]

    # 取得現在時間
    # now = datetime.datetime.now()
    txt = '上次更新時間為：' + str(getNowDatetime())

    # 轉成df
    df = pd.DataFrame([txt], index=['UpdateTime'])

    # 存出檔案
    df.to_csv('log_{0}.csv'.format(os.path.basename(FileFullName).split('.')[0]) , header=False)



#回傳Stock專案時間文字格式(2024-05-31T21:07:35)
def getNowDatetime():
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

#回傳Stock專案時間文字格式(20240531)
def getNowDate():
    return datetime.now().strftime("%Y%m%d")


# 16位timestamp（微秒）時間搓轉回傳Stock專案時間文字格式(2024-05-31T21:07:35)
def timestamp_microToDatetime(timestamp_micro):
    # 假設這是你的 16 位 timestamp（微秒）
    #timestamp_micro = 1713335681123456

    # 轉換成 datetime（除以 1_000_000 變成秒）
    dt = datetime.fromtimestamp(timestamp_micro / 1_000_000)

    # print(dt)  # 輸出: 2024-04-17 12:14:41.123456（視數字而定）
    return dt.strftime("%Y-%m-%dT%H:%M:%S")


#discord傳訊息到特定伺服器(StockNofity)，使用WebHook的方式
def notify_discord_webhook(msg):
    url = getenv('StockNotify_WebHookUrl')
    headers = {"Content-Type": "application/json"}
    data = {"content": msg, "username": "StockNotifyBot"}
    res = requests.post(url, headers = headers, json = data)
    if res.status_code in (200, 204):
        print(f"Request fulfilled with response: {res.text}")
    else:
        print(f"Request failed with response: {res.status_code}-{res.text}")

