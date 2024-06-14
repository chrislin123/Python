import pymssql
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy import text
#urlparse
from urllib.parse import quote_plus
#meta
from sqlalchemy import MetaData
from sqlalchemy import Table, Column, Integer, String, MetaData
from sqlalchemy import select,insert
from sqlalchemy.orm import sessionmaker

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


    # meta.create_all(mssql_engine)


    # Session = sessionmaker(bind=create_engine)
    # with Session() as session:
    #     newStockinfo = stockinfos(stockcode = '9999')
    #     session.add(newStockinfo)
    #     session.commit()


    with  mssql_engine.connect() as connection:
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








