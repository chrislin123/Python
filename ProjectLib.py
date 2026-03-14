import os
from datetime import datetime, timedelta

# 讀取機敏設定檔
from dotenv import get_key, load_dotenv


# ProjectInfo 暫時先放這邊
ProjectID = "C10"
ProjectName = "C10系統相關功能"


def getenv(getenv):
    load_dotenv()
    return os.getenv(getenv)


# 取得該專案Logger寄送mail的設定檔
def getLoggerMailSetting():
    MailSetting = {
        "mail_host": ("smtp.gmail.com", 587),
        "from_addr": getenv("SMTP_USER"),
        "to_addrs": getenv("MAILTO"),
        "subject": f"[{ProjectID}]({ProjectName})系統錯誤通報",
        "credentials": (
            getenv("SMTP_USER"),
            getenv("SMTP_PASSWORD"),
        ),  # 需使用應用程式密碼
    }

    return MailSetting
