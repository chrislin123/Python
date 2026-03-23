import requests
import json
import time
from datetime import datetime, timezone, timedelta
import StockLib

# Logger
from logger import get_logger

log_obj = get_logger()

# 1. 配置與參數
cookie = {
    "substack.sid": "s%3A83QnshvWrWbPZfejKxJ_RgljF7f34xIB.IOzO3kAddYYMJQDAW3%2B8myRNuKqcgunlBU7Mr7NdwiM"
}

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept": "application/json",
    "Referer": "https://substack.com/",
}


def Get_Recent_commentID():
    commentID = ""
    # 取得最新的小黑屋清單ID

    # 1. 取得目前 UTC 時間
    now = datetime.now(timezone.utc)

    # 2. 減去 5 天
    five_days_ago = now - timedelta(days=5)
    now_gmt = five_days_ago.isoformat(timespec="milliseconds")

    # 將結尾的 +00:00 取代為 Z
    now_gmt_z = now_gmt.replace("+00:00", "Z")
    current_before = now_gmt_z

    # current_before = "2026-01-15T07:24:44.054Z"
    url_before = f"https://substack.com/api/v1/community/posts/a3398a1f-1b7c-424d-a713-82c24be32925/comments"
    params = {"order": "desc", "after": current_before, "limit": 50}
    resp = requests.get(
        url_before, headers=headers, cookies=cookie, params=params, timeout=10
    )

    if resp.status_code == 200:
        data = resp.json()

        # --- 改用 replies 欄位作為判斷依據 ---
        # replies_list = data.get("replies", [])
        target_id = 170314954
        replies = data.get("replies", [])

        # 1. 篩選條件：user_id 為 170314954 且 body 不為 Null
        filtered_replies = []

        for r in replies:
            comment = r.get("comment", {})
            user = r.get("user", {})

            # 取得 ID 並強制轉為 int 進行比較，避免 "170314954" == 170314954 判定為 False 的問題
            u_id = comment.get("user_id")
            body = comment.get("body")

            # 檢查條件：ID 匹配、Body 不為空、且不是字串形式的 "null"
            if u_id is not None and int(u_id) == target_id:
                if body is not None and body.strip() != "":
                    filtered_replies.append(r)

        # 2. 找出最近的資料 (依照 created_at 排序)
        if filtered_replies:
            # 使用 datetime.fromisoformat 將 ISO 時間字串轉為可比較的物件
            # 注意：Z 代表 UTC，在 Python 3.11+ 可直接處理，舊版本可能需要替換
            latest_reply = max(
                filtered_replies,
                key=lambda x: datetime.fromisoformat(
                    x["comment"]["created_at"].replace("Z", "+00:00")
                ),
            )

            print(f"找到最接近的資料 ID: {latest_reply['comment']['id']}")
            print(f"時間: {latest_reply['comment']['created_at']}")
            print(f"內容: {latest_reply['comment']['body']}")

            commentID = latest_reply["comment"]["id"]
        else:
            print("沒有符合條件的資料")

    return commentID


def fetch_latest_comments():

    # 初始取得一次
    commentID = Get_Recent_commentID()

    # 記錄上次更新 commentID 的時間
    last_id_update_time = datetime.now()

    # 初始時間點（監控新留言用）
    now_gmt = datetime.now(timezone.utc).isoformat(timespec="milliseconds")
    current_after = now_gmt.replace("+00:00", "Z")

    # test
    # current_after = "2026-01-18T07:24:44.054Z"

    # 這是你指定的對話分支 URL
    url = f"https://substack.com/api/v1/community/comments/{commentID}/comments"

    print(
        f"🚀 監控啟動... 起始 ID: {commentID} | 起始時間: {current_after}\n" + "-" * 50
    )

    while True:
        now = datetime.now()

        # --- 新增：定時更新 commentID 的邏輯 ---
        # 判斷是否在 04:30 - 08:30 之間
        is_update_window = (
            (now.hour == 4 and now.minute >= 30)
            or (5 <= now.hour <= 7)
            or (now.hour == 8 and now.minute <= 30)
        )

        # 如果在時段內，且距離上次更新已超過 10 分鐘
        if is_update_window and (now - last_id_update_time).total_seconds() >= 600:
            print(f"🕒 時段內自動更新 commentID...")
            new_id = Get_Recent_commentID()
            if new_id and new_id != commentID:
                commentID = new_id
                url = f"https://substack.com/api/v1/community/comments/{commentID}/comments"
                print(f"💡 commentID 已更新為: {commentID}")
            last_id_update_time = now
        # ---------------------------------------

        try:
            params = {"order": "asc", "after": current_after, "limit": 50}
            resp = requests.get(
                url, headers=headers, cookies=cookie, params=params, timeout=10
            )

            print(
                f"🔍 [檢查更新] 執行時間- {datetime.now().strftime('%H:%M:%S')} - 參數時間：{current_after}"
            )

            if resp.status_code == 200:
                data = resp.json()

                # --- 改用 replies 欄位作為判斷依據 ---
                replies_list = data.get("replies", [])

                if not replies_list:
                    # 如果這次請求沒有新回覆，不執行動作
                    pass
                else:
                    for item in replies_list:
                        # 結構解析：item 通常包含一個 "comment" 物件與 "user" 物件
                        comment_obj = item.get("comment", {})
                        user_obj = item.get("user", {})

                        user_name = user_obj.get("name", "未知用戶")
                        if not comment_obj.get("body", ""):
                            continue
                        body = comment_obj.get("body", "").strip()
                        date = StockLib.DatetimeString_Trans_UTCtoGMT8(
                            comment_obj.get("created_at", "")
                        )

                        # 重要：更新下一次請求的基準時間點
                        current_after = add_1ms_to_iso(
                            comment_obj.get("created_at", "")
                        )

                        # 格式化輸出（這會正確處理中文轉碼）
                        if body:  # 確保有文字內容內容再列印
                            print(f"💬 新回覆 | [{date[11:19]}] {user_name}: {body}")

                        # current_after = date

                        # Discord-Substack
                        StockLib.notify_discord_webhook(
                            f"[{user_name}]:\n{body}",
                            StockLib.getenv("StockNotify_WebHookUrl_Substack"),
                        )

                        # "大叔"留言在專屬的頻道
                        if user_name == "大叔美股筆記 Uncle Stock Notes":
                            StockLib.notify_discord_webhook(
                                f"[{user_name}]:\n{body}",
                                StockLib.getenv("StockNotify_WebHookUrl_Uncle"),
                            )

                        # "lawrence"留言在專屬的頻道
                        if user_name == "lawrence":
                            StockLib.notify_discord_webhook(
                                f"[{user_name}]:\n{body}",
                                StockLib.getenv("StockNotify_WebHookUrl_lawrence"),
                            )

                        # 存檔 (ensure_ascii=False 解決 Notepad++ 亂碼)
                        # with open("live_chat_log.json", "a", encoding="utf-8") as f:
                        #     log_entry = {"time": date, "user": user_name, "text": body}
                        #     f.write(json.dumps(log_entry, ensure_ascii=False) + "\n")

            elif resp.status_code == 403:
                print("❌ 錯誤：SID 已失效，請更換 Cookie。")
                break
            else:
                print(f"❌ 伺服器回傳狀態碼: {resp.status_code}")

        except Exception as e:
            print(f"⚠️ 發生異常: {e}")
            log_obj.write_log_exception(
                f"異常內容：{e}",
                f"發生異常: {type(e).__name__}",
            )

        # 設定檢查頻率
        time.sleep(30)


def add_1ms_to_iso(utc_str):
    if not utc_str:
        return utc_str
    try:
        dt = datetime.strptime(utc_str.replace("Z", ""), "%Y-%m-%dT%H:%M:%S.%f")
        dt_plus_1ms = dt + timedelta(milliseconds=1)
        return dt_plus_1ms.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3] + "Z"
    except Exception:
        return utc_str


if __name__ == "__main__":

    fetch_latest_comments()
