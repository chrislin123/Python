from datetime import datetime

import pymssql

#urlparse
from urllib.parse import quote_plus

#sqlalchemy
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy import Table, Column, Integer, String, MetaData, Text
from sqlalchemy import select,insert
from sqlalchemy.orm import sessionmaker ,DeclarativeBase
from sqlalchemy.sql import text


class Base(DeclarativeBase):
    pass

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





meta = MetaData()

stockinfos = Table(
    'stockinfo',
    meta,
    Column('no', Integer, primary_key = True),
    Column('stockcode', String),
    Column('stockname', String),
    Column('type', String),
    Column('industry', String),
    Column('updatetime', String),
    Column('status', String),
    Column('updstatus', String),
)





print(sqlalchemy.__version__)




# 原始DBAPI的設定
# db_conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';DATABASE='+database+';UID='+username+';PWD='+ password)

try:

    # connection_str = connection_format.format(db_user,db_password,db_host,db_name)
    # dsn_str = '?driver=ODBC+Driver+17+for+SQL+Server'
    # mssql_engine = create_engine(f'mssql+pyodbc://sa:wistron888@10.34.124.114/master{dsn_str}', echo=True) # echo標誌是設置SQLAlchemy日誌記錄的快捷方式

    connection_format = 'mssql+pymssql://{0}:{1}@{2}/{3}?charset=utf8'
    connection_str = connection_format.format('sa',quote_plus("pass@word1"),'10.8.0.6','C10')
    mssql_engine = create_engine(connection_str, echo=False) # echo標誌是設置SQLAlchemy日誌記錄的快捷方式


    Session = sessionmaker(bind=mssql_engine)

    with Session() as session:
        now = datetime.now()
        date_time = now.strftime("%Y-%m-%dT%H:%M:%S")
        print("date and time:",date_time)



        #execute執行
        params =  { "updstatus": "Y","updatetime":date_time}
        sql = text(" update stockinfo set  updatetime = :updatetime where updstatus = :updstatus ")
        session.execute(sql,params)

        #新增
        # welcome_article = Article(stockcode='9999', stockname='This is my first article')
        # session.add(welcome_article)
        # # session.add_all([welcome_article])

        #更新
        # article = session.query(stockinfo).filter(stockinfo.stockcode == '999991').first()
        # if article == None:
        #     article = stockinfo()
        #     article.stockcode = '999991'
        #     article.stockname = 'test1'
        #     article.updatetime = date_time
        #     session.add(article)
        # else:
        #     article.stockname = 'test2'
        #     article.updatetime = date_time

        # sql = """ update stockinfo set stockcode = '999991' where updstatus = 'N' """
        # query = session.execute.execute(sql)


        #刪除
        # article = session.query(stockinfo).filter(stockinfo.stockcode == '999991').first()
        # if article != None:
        #     session.delete(article)

        session.commit()


    # meta.create_all(mssql_engine)


    # Session = sessionmaker(bind=create_engine)
    # with Session() as session:
    #     newStockinfo = stockinfos(stockcode = '9999')
    #     session.add(newStockinfo)
    #     session.commit()


    with  mssql_engine.connect() as connection:

        #execute執行
        params =  { "updstatus": "Y","updatetime":date_time}
        sql = """ update stockinfo set stockcode = '99999' where updstatus = 'N' """
        # connection.execute(sql)
        connection.execute(text(" update stockinfo set  updatetime = :updatetime where updstatus = :updstatus ")
                           ,params)
        connection.commit()




        #select
        # sss = select(stockinfos).where(stockinfos.c.stockcode == '2330')
        sss = select(stockinfos).where(stockinfos.c.stockcode == '2330')
        # sss = select([stockinfos.c.stockcode,stockinfos.c.stockname]).where(stockinfos.c.stockcode == '2330')
        result = connection.execute(sss)
        for row in result:
                # print("username:", row['username'])
            print(row)

        #insert

        # ins = stockinfos.insert().values(stockcode = '9999')
        # # ins = stockinfos.insert(stockinfos.c.stockcode = '9999')
        # print(ins)
        # ins.compile.params
        # print(ins)

        # result = connection.execute(ins)

        result = connection.execute(
            # insert(stockinfos)
            stockinfos.insert()
            ,[
                {"stockcode":"99999", "stockname": "estInsert"},
                # {"stockcode":"10000", "stockname": "estInsert"},

            ]
        )
        connection.commit()






    # print(type(mssql_engine))
    # print('Connect [MSSQL] database successfully!')

    # with  mssql_engine.connect() as connection:
    #     # result = connection.execute(" select * from StockInfo ")
    #     query = "select * from StockInfo"
    #     result = connection.execute(text(query))


    #     for row in result:
    #         # print("username:", row['username'])
    #         print(row.stockcode)





    # connection.close()



except Exception as e:
    print(f"Encounter exception: {e}")
finally:
    # 斷開資料庫的連線
    mssql_engine.dispose()








