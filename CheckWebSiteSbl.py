# 分點明細查詢-金額
import os
import sys
import re
import time
import random
import requests
import urllib3
import datetime
from bs4 import BeautifulSoup
import pandas as pd
from lxml import etree, html

# 資料庫相關
# import pymssql
from collections import deque

import AppSetting as AppS

# StockLib
from StockLib import LogRunTimeToCsv, getenv
import StockLib as StockLib

# LineLib
from LineLib import PushMessageEarn2

# mail
from mail import SendGmail
from pathlib import Path


# 避免requests中設定verify=False，會出現錯誤訊息的問題(不過看起來只是隱藏錯誤訊息)，待查明
urllib3.disable_warnings()

# print(f"[checkWebSiteSbl]開始執行")

# 啟動後，三分鐘內隨機啟動，避免被發現規律爬蟲
if AppS.ProductionEnv == True:
    time.sleep(random.randint(1, 30))


# 在本機紀錄執行時間
# LogRunTimeToCsv(None,__file__)


from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.keys import Keys
from webdriver_manager.chrome import ChromeDriverManager


def checkWebSiteSbl():
    """設定 Chrome WebDriver"""
    # Define the path to your custom user data directory
    # You can create a new directory or use an existing one
    user_data_dir = os.path.join(os.getcwd(), "selenium_user_data")

    # Ensure the directory exists
    os.makedirs(user_data_dir, exist_ok=True)

    options = Options()
    prefs = {
        # "download.default_directory": str(DOWNLOAD_DIR),
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
    }
    options.add_experimental_option("prefs", prefs)
    options.add_argument(f"--user-data-dir={user_data_dir}")
    options.add_argument("--disable-notifications")
    options.add_argument("--disable-popup-blocking")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    # if self.settings.get('headless', False):
    #     options.add_argument('--headless')

    # if 'user_agent' in self.settings:
    #     options.add_argument(f'--user-agent={self.settings["user_agent"]}')
    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    element_value = ""
    try:
        # 用來阻止網站偵測到瀏覽器正在自動化
        driver.execute_script(
            "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
        )

        driver.get(
            "https://www.tpex.org.tw/zh-tw/mainboard/trading/margin-trading/sbl.html"
        )
        # 讀取網頁
        time.sleep(5)

        # 日期元件的value
        element = driver.find_element(By.ID, "___auto1")
        element_value = element.get_attribute("value")
        print(element_value)

    except Exception as e:
        # logging.error(f"Chrome WebDriver 初始化失敗: {e}")
        raise
    finally:
        if driver:
            driver.quit()

    # 讀取檔案比對資料是否異動
    try:
        current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
        log_FilePaht = current_dir / "log" / "CheckWebSiteSbl.txt"

        if os.path.exists(log_FilePaht) == False:
            with open(log_FilePaht, "w") as file:
                file.write("")
        data_to_save = ""
        with open(log_FilePaht, "r") as file:
            data_to_save = file.read()

        if data_to_save != element_value:
            # 傳送訊息
            print(
                f"證卷櫃檯買賣中心-信用額度總量管制餘額表 更新：{data_to_save}=>{element_value}"
            )
            StockLib.notify_discord_webhook(
                f"證卷櫃檯買賣中心-信用額度總量管制餘額表 更新：{data_to_save}=>{element_value}"
            )
            # 紀錄
            with open(log_FilePaht, "w") as file:
                file.write(element_value)

        print(f"證卷櫃檯買賣中心-信用額度總量管制餘額表 偵測完成")
        # element_value = ""
    except Exception as e:
        raise


if __name__ == "__main__":
    checkWebSiteSbl()
