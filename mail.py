from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import smtplib

from StockLib import getenv

def SendGmail(MailTo,Title,Content):

    #取得機敏資料
    SMTP_USER = getenv('SMTP_USER')
    SMTP_PASSWORD = getenv('SMTP_PASSWORD')

    content = MIMEMultipart()  #建立MIMEMultipart物件
    content["subject"] = Title  #郵件標題
    content["from"] = SMTP_USER  #寄件者
    content["to"] = MailTo #收件者
    content.attach(MIMEText(Content))  #郵件內容



    with smtplib.SMTP(host="smtp.gmail.com", port="587") as smtp:  # 設定SMTP伺服器
        try:
            smtp.ehlo()  # 驗證SMTP伺服器
            smtp.starttls()  # 建立加密傳輸
            smtp.login(SMTP_USER, SMTP_PASSWORD)  # 登入寄件者gmail
            smtp.send_message(content)  # 寄送郵件
            print("Complete!")
        except Exception as e:
            print("Error message: ", e)

##引用範例##
# #mail
# from mail import SendGmail
# SendGmail('chris.lin.tw123@gmail.com', 'My Python Test send', 'Test content')
