from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
import smtplib
import os
from StockLib import getenv


def SendGmail(MailTo, Title, Content):

    # 取得機敏資料
    SMTP_USER = getenv("SMTP_USER")
    SMTP_PASSWORD = getenv("SMTP_PASSWORD")

    content = MIMEMultipart()  # 建立MIMEMultipart物件
    content["subject"] = Title  # 郵件標題
    content["from"] = SMTP_USER  # 寄件者
    content["to"] = MailTo  # 收件者
    content.attach(MIMEText(Content))  # 郵件內容

    with smtplib.SMTP(host="smtp.gmail.com", port="587") as smtp:  # 設定SMTP伺服器
        try:
            smtp.ehlo()  # 驗證SMTP伺服器
            smtp.starttls()  # 建立加密傳輸
            smtp.login(SMTP_USER, SMTP_PASSWORD)  # 登入寄件者gmail
            smtp.send_message(content)  # 寄送郵件
            print("Complete!")
        except Exception as e:
            print("Error message: ", e)


def SendGmailWithImage(MailTo, Title, Content, ImagePath=None):
    SMTP_USER = getenv("SMTP_USER")
    SMTP_PASSWORD = getenv("SMTP_PASSWORD")

    content = MIMEMultipart("related")  # 改用 related 類型以支援內嵌圖片
    content["subject"] = Title
    content["from"] = SMTP_USER
    content["to"] = MailTo

    # 建立 HTML 內容，使用 <img src="cid:image1"> 來引用圖片
    html_content = f"""
    <html>
      <body>
        <p>{Content.replace('\n', '<br>')}</p>
        {f'<br><img src="cid:image1"><br>' if ImagePath else ''}
        <p style="color:gray;">-- 由 Python 自動化系統發送 --</p>
      </body>
    </html>
    """
    content.attach(MIMEText(html_content, "html"))

    # 如果有圖片路徑，則附加圖片並設定 Content-ID
    if ImagePath and os.path.exists(ImagePath):
        with open(ImagePath, "rb") as f:
            img_data = f.read()
            img = MIMEImage(img_data)
            img.add_header("Content-ID", "<image1>")  # 這對應 HTML 中的 cid:image1
            content.attach(img)

    with smtplib.SMTP(host="smtp.gmail.com", port="587") as smtp:
        try:
            smtp.ehlo()
            smtp.starttls()
            smtp.login(SMTP_USER, SMTP_PASSWORD)
            smtp.send_message(content)
            print("Email with Image Sent Complete!")
        except Exception as e:
            print("Error message: ", e)


##引用範例##
# #mail
# from mail import SendGmail
# SendGmail('chris.lin.tw123@gmail.com', 'My Python Test send', 'Test content')
