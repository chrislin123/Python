import os
import requests
import StockLib
import random
from datetime import datetime
from pathlib import Path
import json

# https://discord.com/api/webhooks/1363216809817407709/EKxGlWzS9vMv_JxPnWbP8j326xymBiCiup0pOg55xhl5rGcIJAC-cIgd4DM8BucorUfn


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
        # 1. Send the GET request
        response = requests.get(api_url, headers={"User-Agent": _get_user_agent()})
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
            StockLib.notify_discord_webhook(sResult)

        print(f"[CNN-恐慌指數]{NewData["timestamp"]}=({rating})-{score}")

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")


# 直接執行這個模組，它會判斷為 true
# 從另一個模組匯入這個模組，它會判斷為 false
if __name__ == "__main__":
    procfearandgreed()
