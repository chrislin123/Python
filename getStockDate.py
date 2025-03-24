#
# Python 取得台指期結算日



# from datetime import datetime, timedelta

# def get_tx_settlement_date(year, month):
#     """計算指定年月的台指期結算日（每月第三個星期三）"""
#     first_day = datetime(year, month, 1)  # 當月第一天
#     weekday = first_day.weekday()  # 0 = 星期一, 1 = 星期二, ..., 6 = 星期日
#     first_wednesday = 3 - weekday if weekday <= 2 else 10 - weekday
#     settlement_day = first_day + timedelta(days=first_wednesday + 14)  # 第三個星期三
#     return settlement_day.strftime("%Y-%m-%d")  # 轉換為字串

# # 取得當月台指期結算日
# today = datetime.today()
# settlement_date = get_tx_settlement_date(today.year, today.month)
# print(f"台指期結算日: {settlement_date}")




from datetime import datetime
from dateutil.relativedelta import relativedelta, WE

def get_tx_settlement_date(year, month):
    """計算台指期結算日（每月第三個星期三）"""
    third_wednesday = datetime(year, month, 1) + relativedelta(weekday=WE(3))  # 第三個星期三
    return third_wednesday.strftime("%Y-%m-%d")

# 取得當月台指期結算日
today = datetime.today()
settlement_date = get_tx_settlement_date(today.year, today.month)
settlement_date = get_tx_settlement_date(2025, 12)
print(f"台指期結算日: {settlement_date}")