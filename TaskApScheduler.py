from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime, timedelta
import time
from GetStockAfter import getStockAfter

def alarm(time):
    # print("現在時間 %s" % time)
    print("現在時間 %s" % datetime.now())



scheduler = BlockingScheduler()

#scheduler.add_jobstore("sqlalchemy", url="sqlite:///schedule.sqlite3")

#print("現在時間 %s" % datetime.now())
# alarm_time = datetime.now() + timedelta(seconds=10)

# scheduler.add_job(alarm, 'date', run_date = alarm_time, args=[datetime.now()])

#scheduler.add_job(getStockAfter, 'interval', seconds=10, args=[datetime.now()])  # 每 10 秒執行一次

#scheduler.add_job(getStockAfter, 'cron', hour='2', minute='19', args=[datetime.now()])  # 每 10 秒執行一次
#啟動每日排程
#14:30=每日取得盤後股價
scheduler.add_job(getStockAfter, 'cron', hour='14', minute='30')

print("scheduler 開始執行，現在時間 %s" % datetime.now())
scheduler.start()
print("scheduler 開始執行，現在時間 %s" % datetime.now())
