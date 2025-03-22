from linebot import LineBotApi
from linebot.models import TextSendMessage

from StockLib import getenv



def PushMessage(LineToUser,Message):
    # 設定你的Channel Access Token
    CHANNEL_ACCESS_TOKEN = getenv("CHANNEL_ACCESS_TOKEN")
    # 用戶ID，這是你想要發送訊息的用戶
    #user_id = ""

    # 創建Line Bot API物件
    line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN)
    # 要發送的訊息
    message = TextSendMessage(text=Message)

    # 發送訊息
    line_bot_api.push_message(LineToUser, messages=message)


#for 賺豹2
def PushMessageEarn2(Message):
    USER_ID = getenv("LINEUSER_EARN")
    PushMessage(USER_ID,Message)

