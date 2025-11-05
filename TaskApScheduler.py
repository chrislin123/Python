from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.executors.pool import ThreadPoolExecutor, ProcessPoolExecutor
from datetime import datetime, timedelta
import time
import StockLib

from GetStockAfter import getStockAfter
from GetStockInfo import getStockInfo
from ProcCNNFearAndGreed import procfearandgreed

#from CheckWebSiteSbl import checkWebSiteSbl
#from DailyRun import daily_data_updater,daily_otc_updater

def alarm(time):
    # print("現在時間 %s" % time)
    print("現在時間 %s" % datetime.now())

print(f"{StockLib.getNowDatetime()}-啟動準備程序")
# --- 1. 定義執行器配置 ---
executors = {
    # 執行器名稱 'default'，使用 ThreadPoolExecutor
    'default': ThreadPoolExecutor(max_workers=20),
    # 您也可以添加第二個執行器，用於特定任務
    # 'high_priority': ThreadPoolExecutor(max_workers=5)
}

# --- 2. 初始化 Scheduler ---
scheduler = BlockingScheduler(executors=executors)

#scheduler.add_jobstore("sqlalchemy", url="sqlite:///schedule.sqlite3")

#print("現在時間 %s" % datetime.now())
# alarm_time = datetime.now() + timedelta(seconds=10)

# scheduler.add_job(alarm, 'date', run_date = alarm_time, args=[datetime.now()])

#scheduler.add_job(getStockAfter, 'interval', seconds=10, args=[datetime.now()])  # 每 10 秒執行一次

#scheduler.add_job(getStockAfter, 'cron', hour='2', minute='19', args=[datetime.now()])  # 每 10 秒執行一次


#啟動每日排程
#14:00=每日股票基本資料轉檔
scheduler.add_job(getStockInfo, 'cron', hour='14', minute='00',misfire_grace_time=3600)

#14:00=每日股票基本資料轉檔
#test
scheduler.add_job(getStockInfo, 'cron', hour='00', minute='20',misfire_grace_time=3600)

#14:30=每日取得盤後股價
scheduler.add_job(getStockAfter, 'cron', hour='14', minute='30',misfire_grace_time=3600)

#每 1分執行一次=CNN恐慌指數
scheduler.add_job(procfearandgreed, 'interval', seconds=60 ,misfire_grace_time=3600)  


#台灣證券交易所-信用額度總量管制餘額表
#每天 20:35 及 22:35 各執行一次
#scheduler.add_job(daily_data_updater.getdaily_data_updater, 'cron', hour='20,22', minute='35',misfire_grace_time=3600)

#證卷櫃檯買賣中心-信用額度總量管制餘額表
#每天 20:35 及 22:35 各執行一次
#scheduler.add_job(daily_otc_updater.getdaily_otc_updater, 'cron', hour='20,22', minute='35',misfire_grace_time=3600)

#證卷櫃檯買賣中心-信用額度總量管制餘額表=偵測時間更新
#scheduler.add_job(checkWebSiteSbl, 'interval', seconds=60, args=[])  # 每 10 分執行一次


print(f"{StockLib.getNowDatetime()}-scheduler 批次排程啟動")
scheduler.start()

