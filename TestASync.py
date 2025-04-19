
from time import sleep

# def hello_world():
#     print("Hello")
#     sleep(1)
#     print("World")

# hello_world()
# hello_world()
# hello_world()

#資料庫連線相關及Orm.Model
from db import dbinst,StockBroker1,StockBrokerBS,StockLog

import StockLib as StockLib
import sys
import asyncio
import datetime










async def MaxVol2330(data):
    try:

        async with dbinst.get_asyncsession()() as session:

            Stocklog = StockLog()
            Stocklog.logtype = 'TestASync'
            Stocklog.logdate = '20250417'
            Stocklog.key1 = ''
            Stocklog.key2 = data['test']
            Stocklog.logstatus = 'true'
            Stocklog.memo = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')
            Stocklog.logdatetime = StockLib.getNowDatetime()
            session.add(Stocklog)
            await session.commit()

    except Exception as e:
        trace_back = sys.exc_info()[2]
        line = trace_back.tb_lineno
        print('{0}，Error Line:{1}'.format(f"Encounter exception: {e}"),line)


async def hello_world():
    print("Hello")
    # # 模擬一個非同步 I/O 操作，這裡使用 asyncio.sleep 來模擬等待操作
    #await asyncio.sleep(2)

    data = {}
    data['test'] = '2330'
    await MaxVol2330(data)


    print("World")


async def main():
    # 使用 asyncio.gather 同時執行多個協程
    # await asyncio.gather(hello_world(), hello_world(), hello_world(), hello_world(), hello_world(), hello_world(), hello_world(), hello_world(), hello_world())
    await asyncio.gather(hello_world())
    # print("S")
    # loop = asyncio.get_running_loop()  # 獲取當前事件迴圈
    # task1_future = loop.create_task(hello_world())  # 建立任務 1
    # task2_future = loop.create_task(hello_world())  # 建立任務 2
    # await task1_future
    # await task2_future
    # print("E")







asyncio.run(main())



# # 創建事件循環
# loop = asyncio.get_event_loop()

# # 使用 run_until_complete 啟動 main 協程
# loop.run_until_complete(main())

# # 關閉事件循環
# loop.close()
