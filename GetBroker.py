import io
import re
import requests
import pandas as pd
from datetime import datetime


#資料庫連線相關及Orm.Model
from db import dbinst,StockBroker,StockBroker1



# #卷商基本資料網址
# url = "https://www.twse.com.tw/rwd/zh/brokerService/outPutExcel"

# #讀取網址下載EXCEL(xls)
# s=requests.get(url).content
# xl = pd.ExcelFile(s)

# #取得該SHEET資料
# df = pd.read_excel(xl,'證券商基本資料')


# #寫入資料庫
# try:
#     connection_format = 'mssql+pymssql://{0}:{1}@{2}/{3}?charset=utf8'
#     connection_str = connection_format.format('sa',quote_plus("pass@word1"),'10.8.0.6','C10')
#     mssql_engine = create_engine(connection_str, echo=False) # echo標誌是設置SQLAlchemy日誌記錄的快捷方式
#     Session = sessionmaker(bind=mssql_engine)

#     with Session() as session:
#         for row in df.values:
#             print(row)
#             now = datetime.now()
#             date_time = now.strftime("%Y-%m-%dT%H:%M:%S")

#             article = session.query(StockBroker).filter(StockBroker.brokercode == row[0]).first()
#             if article == None:
#                 article = StockBroker()
#                 article.brokercode = row[0]
#                 article.brokername = row[1]
#                 article.updatetime = date_time
#                 session.add(article)

#             else:
#                 article.stockname = row[1]
#                 article.updatetime = date_time

#             session.commit()

# except Exception as e:
#     print(f"Encounter exception: {e}")
# finally:
#     # 斷開資料庫的連線
#     mssql_engine.dispose()



#20240526 使用元富證卷進行解析查詢
# http://newjust.masterlink.com.tw/z/zg/zgb/zgb0.djhtm
#取得卷商及分點
#先由預設網頁取得卷商清單

header = {
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
}

# requests.encoding = 'big5'
# 原本網頁中的JS就有包含所有的券商及分點的名稱及代碼
BrokerList_URL = 'https://newjust.masterlink.com.tw/z/js/zbrokerjs.djjs'
res = requests.get(BrokerList_URL, headers=header)
res.encoding = res.apparent_encoding
#拆解主要文字，只取需要的文字
brokerText = re.split("'", res.text.partition('\n')[0])[1]
#取得卷商
brokerText1 = re.split(";", brokerText)
#取得分點
brokerText2 = re.split("!", brokerText1[0])
#取得分點名稱及代碼
brokerText3 = re.split(",", brokerText2[0])


#寫入資料庫
try:
    with dbinst.getsession()() as session:


        #取得卷商
        for row1 in re.split(";", brokerText):
            iIndex = 0
            sParentCode = ''

            for row2 in re.split("!", row1):

                print(row2)

                date_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

                broker = re.split(",", row2)
                BrokerItem = StockBroker1()
                BrokerItem.brokercode = broker[0]
                BrokerItem.brokername = broker[1]
                BrokerItem.updatetime = date_time
                if iIndex == 0:
                    BrokerItem.brokerparentyn = 'Y'
                    BrokerItem.brokerparentcode = broker[0]
                    sParentCode = broker[0]
                else:
                    BrokerItem.brokerparentyn = 'N'
                    BrokerItem.brokerparentcode = sParentCode

                article = session.query(StockBroker1).filter(
                    StockBroker1.brokercode == BrokerItem.brokercode
                    ,StockBroker1.brokerparentyn == BrokerItem.brokerparentyn).first()

                if article == None:
                    article = BrokerItem
                    session.add(article)
                else:
                    article.brokername = BrokerItem.brokername
                    article.brokerparentcode = BrokerItem.brokerparentcode
                    article.brokerparentyn = BrokerItem.brokerparentyn
                    article.updatetime = date_time

                session.commit()

                #
                iIndex += 1

            #每次卷商資料結束，還原序列0
            iIndex = 0

except Exception as e:
    print(f"Encounter exception: {e}")
# finally:
#     # 斷開資料庫的連線
#     mssql_engine.dispose()








sss = ''
# df_deathsAges = pd.read_excel(io.BytesIO(s),
#                           nrows = 25, header = 5, sheet_name='Covid-19 - Weekly occurrences', engine="openpyxl")