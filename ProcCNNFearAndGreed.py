import os
import requests
import StockLib
import random
from datetime import datetime
from pathlib import Path
import json
import ProjectLib

# https://discord.com/api/webhooks/1363216809817407709/EKxGlWzS9vMv_JxPnWbP8j326xymBiCiup0pOg55xhl5rGcIJAC-cIgd4DM8BucorUfn

# Logger
from logger import WriteLogTxt

log_obj = WriteLogTxt(r"\logs\TaskLog", "TaskLog", ProjectLib.getLoggerMailSetting())
log_obj.setup_logger()


def procfearandgreed():

    OldData = {"score": "", "rating": "", "timestamp": ""}
    NewData = {"score": "", "rating": "", "timestamp": ""}

    current_dir = Path(os.path.dirname(os.path.abspath(__file__)))
    log_Path = f"{current_dir}/localdata"
    Path(log_Path).mkdir(parents=True, exist_ok=True)
    log_FilePath = f"{current_dir}/localdata/CNNFearAndGreed.txt"
    if os.path.exists(log_FilePath) == False:
        with open(log_FilePath, "w") as file:
            # 沒資料寫入預設值
            file.write(json.dumps(OldData, indent=4))

    with open(log_FilePath, "r") as file:
        OldData = json.loads(file.read())

    # 格式化URL所需要的時間點
    QueryDate = datetime.now().strftime("%Y-%m-%d")
    # The URL of the API endpoint you want to query
    api_url = (
        f"https://production.dataviz.cnn.io/index/fearandgreed/graphdata/{QueryDate}"
    )

    try:
        headers = {
            "User-Agent": StockLib._get_user_agent(),
            "Accept": "application/json",
            "Referer": "https://www.cnn.com/markets/fear-and-greed",
            "Origin": "https://www.cnn.com",
        }

        # 1. Send the GET request
        response = requests.get(
            api_url,
            headers=headers,
            timeout=20,  # 20秒沒回應就報錯跳出
        )
        # Check if the request was successful (status code 200)
        response.raise_for_status()

        # 2. Get the JSON data as a Python dictionary/list
        data = response.json()

        score = data["fear_and_greed"]["score"]
        rating = data["fear_and_greed"]["rating"]

        # 恐慌指數，四捨五入取整數
        float_num = float(score)
        score = round(float_num)

        NewData["score"] = str(score)
        NewData["rating"] = rating
        NewData["timestamp"] = StockLib.getNowDatetime()

        # 結果儲存在本地端，依照不同條件傳送訊息
        # 寫入本地資料
        with open(log_FilePath, "w") as file:
            # 沒資料寫入預設值
            file.write(json.dumps(NewData, indent=4))

        # todo 判斷傳送時機(層級變動或是數據變動)
        if (
            NewData["rating"] != OldData["rating"]
            or NewData["score"] != OldData["score"]
        ):
            # 傳送訊息到discord
            sResult = f"[CNN-恐慌指數]({rating})-{score}"
            StockLib.notify_discord_webhook(
                sResult,
                StockLib.getenv("StockNotify_WebHookUrl_cnn"),
            )

        print(f"[CNN-恐慌指數]{NewData["timestamp"]}=({rating})-{score}")
    except requests.exceptions.Timeout as eTimeout:
        print("Timeout Error: CNN server took too long to respond.")
        log_obj.write_log_exception(
            f"異常內容：{eTimeout}",
            f"Timeout Error: CNN server took too long to respond.",
        )
    except Exception as e:
        log_obj.write_log_exception(
            f"異常內容：{e}",
            f"發生異常: {type(e).__name__}",
        )
        print(f"An error occurred: {e}")


# 直接執行這個模組，它會判斷為 true
# 從另一個模組匯入這個模組，它會判斷為 false
if __name__ == "__main__":
    procfearandgreed()
