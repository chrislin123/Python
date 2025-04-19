
import pymssql
from collections import deque

#AppSetting
import AppSetting as AppS

#urlparse
from urllib.parse import quote_plus

#資料庫相關sqlalchemy
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData, Text,DateTime
from sqlalchemy import select,insert
from sqlalchemy.orm import sessionmaker ,DeclarativeBase
from sqlalchemy.sql import text
from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio import create_async_engine,AsyncSession




#產生資料庫連線的類別
class dbinst():


    def __init__(self) -> None:
        pass

    def getsession():
        connection_format = 'mssql+pymssql://{0}:{1}@{2}/{3}?charset=utf8'
        connection_str = connection_format.format('sa',quote_plus("pass@word1"),AppS.DataBaseIP,'C10')
        # echo標誌是設置SQLAlchemy日誌記錄的快捷方式
        #使用NullPool，則session結束的時候就關閉連線，否則要等engine關閉或是程式關閉，連線才會停止
        mssql_engine = create_engine(connection_str, echo=False ,poolclass=NullPool )
        return sessionmaker(bind=mssql_engine)

    def get_asyncsession():
        #MSSQL 非同步連線需要使用ODBC Driver(aioodbc)
        DB_USER = "sa"
        DB_PASSWORD = "pass@word1"
        DB_HOST = "10.8.0.6"
        DB_NAME = "C10"
        driver = "ODBC Driver 17 for SQL Server"
        connection_str = (
            f"mssql+aioodbc://{DB_USER}:{quote_plus(DB_PASSWORD)}@{DB_HOST}/{DB_NAME}"
            f"?driver={quote_plus(driver)}"
        )

        # echo標誌是設置SQLAlchemy日誌記錄的快捷方式
        #使用NullPool，則session結束的時候就關閉連線，否則要等engine關閉或是程式關閉，連線才會停止
        mssql_engine = create_async_engine(connection_str, echo=False ,poolclass=NullPool )
        return sessionmaker(bind=mssql_engine,class_=AsyncSession)



#================= ORM.Model =================
class Base(DeclarativeBase):
    pass

#個股基本資料
class stockinfo(Base):
    __tablename__ = 'stockinfo'
    no = Column(Integer, primary_key=True, autoincrement=True)
    stockcode = Column(Text)
    stockname = Column(Text)
    type = Column(Text)
    industry = Column(Text)
    updatetime = Column(Text)
    status = Column(Text)
    updstatus = Column(Text)

#個股盤後資料
class StockAfter(Base):
    __tablename__ = 'StockAfter'
    no = Column(Integer, primary_key=True, autoincrement=True)
    stockcode = Column(Text)
    stockdate = Column(Text)
    openPrice = Column(Text)
    highPrice = Column(Text)
    lowPrice = Column(Text)
    closePrice = Column(Text)
    change = Column(Text)
    changePercent = Column(Text)
    tradeVolume = Column(Text)
    tradeValue = Column(Text)
    updatetime = Column(Text)

#卷商分點每日買賣資料-張數
class StockBrokerBS(Base):
    __tablename__ = 'StockBrokerBS'
    no = Column(Integer, primary_key=True, autoincrement=True)
    brokercode = Column(Text)
    stockcode = Column(Text)
    stockdate = Column(Text)
    isbuyover = Column(Text)
    buyvol = Column(Integer,default=0)
    sellvol = Column(Integer,default=0)
    diffvol = Column(Integer,default=0)
    updatetime = Column(Text)

#卷商分點每日買賣資料-金額
class StockBrokerBSAmo(Base):
    __tablename__ = 'StockBrokerBSAmo'
    no = Column(Integer, primary_key=True, autoincrement=True)
    brokercode = Column(Text)
    stockcode = Column(Text)
    stockdate = Column(Text)
    isbuyover = Column(Text)
    buyamo = Column(Integer,default=0)
    sellamo = Column(Integer,default=0)
    diffamo = Column(Integer,default=0)
    updatetime = Column(Text)

#卷商分點資料(來源上市上櫃網頁)
class StockBroker(Base):
    __tablename__ = 'StockBroker'
    no = Column(Integer, primary_key=True, autoincrement=True)
    brokercode = Column(Text)
    brokername = Column(Text)
    brokerparent = Column(Text)
    updatetime = Column(Text)

#卷商分點資料(來源元富證卷)
class StockBroker1(Base):
    __tablename__ = 'StockBroker1'
    no = Column(Integer, primary_key=True, autoincrement=True)
    brokercode = Column(Text)
    brokername = Column(Text)
    brokerparentyn = Column(Text)
    brokerparentcode = Column(Text)
    updatetime = Column(Text)

#各項LOG紀錄
class StockLog(Base):
    __tablename__ = 'StockLog'
    no = Column(Integer, primary_key=True, autoincrement=True)
    logtype = Column(Text)
    logdate = Column(Text)
    key1 = Column(Text)
    key2 = Column(Text)
    logstatus = Column(Text)
    memo = Column(Text)
    logdatetime = Column(Text)
#==LOG type 說明 logtype=
# logtype= StockBrokerBSDaily == 卷商分點每日買賣資料-數量
# logtype= StockBrokerBSAmoDaily == 卷商分點每日買賣資料-金額

#個股資料類別
class StockInfoType(Base):
    __tablename__ = 'StockInfoType'
    no = Column(Integer, primary_key=True, autoincrement=True)
    stockcode = Column(Text)
    infotype = Column(Text)
    updatetime = Column(Text)
    status = Column(Text)
    updstatus = Column(Text)
    remark = Column(Text)
#==infotype 說明 infotype=
# infotype= StockFutures == 有股票期貨清單

#個股大單追蹤
class StockMaxVol(Base):
    __tablename__ = 'StockMaxVol'
    no = Column(Integer, primary_key=True, autoincrement=True)
    stockcode = Column(Text)
    stockdate = Column(Text)
    tradedatetime = Column(Text)
    price = Column(Text)
    pricetype = Column(Text)
    unittype = Column(Text)
    size = Column(Text)
    serial = Column(Text)
#==pricetype 說明 pricetype=
# pricetype=> bid-成交於內盤,ask-成交於外盤




#M14-縣市鄉鎮
class CityArea(Base):
    __tablename__ = 'CityArea'
    no = Column(Integer, primary_key=True, autoincrement=True)
    CityName = Column(Text)
    AreaName = Column(Text)
    ZipCode = Column(Text)



class MyClass:
  x = 5

class Dog:
    how = "Test"

    def __init__(self, name, age):
        self.name = name
        self.age = age

    def bark(self):
        print(self.name + "正在叫！")

    def describe(self):
        print(self.name + "的年齡是" + str(self.age) + "歲。")
