import os
from datetime import datetime, timedelta
import requests
import random


import pandas as pd

# 讀取機敏設定檔
from dotenv import get_key, load_dotenv


def getenv(getenv):
    load_dotenv()
    return os.getenv(getenv)


def LogRunTimeToCsv(self, FileFullName):

    # os.path.basename(FileFullName).split('.')[0]

    # 取得現在時間
    # now = datetime.datetime.now()
    txt = "上次更新時間為：" + str(getNowDatetime())

    # 轉成df
    df = pd.DataFrame([txt], index=["UpdateTime"])

    # 存出檔案
    df.to_csv(
        "log_{0}.csv".format(os.path.basename(FileFullName).split(".")[0]), header=False
    )


# 回傳Stock專案時間文字格式(2024-05-31T21:07:35)
def getNowDatetime():
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


# 回傳Stock專案時間文字格式(20240531)
def getNowDate():
    return datetime.now().strftime("%Y%m%d")


# 16位timestamp（微秒）時間搓轉回傳Stock專案時間文字格式(2024-05-31T21:07:35)
def timestamp_microToDatetime(timestamp_micro):
    # 假設這是你的 16 位 timestamp（微秒）
    # timestamp_micro = 1713335681123456

    # 轉換成 datetime（除以 1_000_000 變成秒）
    dt = datetime.fromtimestamp(timestamp_micro / 1_000_000)

    # print(dt)  # 輸出: 2024-04-17 12:14:41.123456（視數字而定）
    return dt.strftime("%Y-%m-%dT%H:%M:%S")


# discord傳訊息到特定伺服器(StockNofity)，使用WebHook的方式
def notify_discord_webhook(msg, url=None):
    # 如果沒有傳WebHook網址，則使用預設
    if url is None:
        url = getenv("StockNotify_WebHookUrl")

    headers = {"Content-Type": "application/json"}
    data = {"content": msg, "username": "StockNotifyBot"}
    res = requests.post(url, headers=headers, json=data)
    if res.status_code in (200, 204):
        s = ""
        # print(f"Request fulfilled with response: {res.text}")
    else:
        print(f"Request failed with response: {res.status_code}-{res.text}")


def _get_user_agent() -> str:
    """Get a random User-Agent strings from a list of some recent real browsers

    Parameters
    ----------
    None

    Returns
    -------
    str
        random User-Agent strings
    """
    user_agent_strings = [
        "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.10; rv:86.1) Gecko/20100101 Firefox/86.1",
        "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:86.1) Gecko/20100101 Firefox/86.1",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.10; rv:82.1) Gecko/20100101 Firefox/82.1",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:86.0) Gecko/20100101 Firefox/86.0",
        "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:86.0) Gecko/20100101 Firefox/86.0",
        "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.10; rv:83.0) Gecko/20100101 Firefox/83.0",
        "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:84.0) Gecko/20100101 Firefox/84.0",
    ]

    return random.choice(user_agent_strings)


def DatetimeString_Trans_UTCtoGMT8(utc_str) -> str:
    # 原始格林威治時間字串
    # utc_str = "2026-01-18T06:33:24.643Z"

    # 1. 解析字串 (將 Z 替換掉以便 strptime 處理)
    # %f 會處理 643 毫秒的部分
    utc_dt = datetime.strptime(utc_str.replace("Z", ""), "%Y-%m-%dT%H:%M:%S.%f")

    # 2. 加上 8 小時轉為 GMT+8
    local_dt = utc_dt + timedelta(hours=8)

    # 3. 轉回字串格式
    local_str = local_dt.strftime("%Y-%m-%d %H:%M:%S.%f")[
        :-3
    ]  # [:-3] 是為了只保留到毫秒

    return local_str
