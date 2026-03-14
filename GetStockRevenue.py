import requests
import pandas as pd
import datetime

# from tqdm import tqdm
import time
from io import StringIO
from bs4 import BeautifulSoup

import StockLib

# 資料庫連線相關及Orm.Model
from db import dbinst, StockRevenueMonth, stockinfo
from sqlalchemy.sql import text


# ------------------------------
# 主程式
# ------------------------------
def crawl_all_revenue(target_year=None, target_month=None):
    # today = datetime.date.today()
    # year = target_year or today.year
    # month = target_month or (today.month - 1 if today.day < 10 else today.month)
    # print(f"📅 抓取 {year} 年 {month} 月 營收資料中...\n")

    # 台灣的上市櫃公司需要在每月10號以前公布上個月的營收
    # 預計規劃，暫定，每月的1號-12號，才開始抓取上個月資料，
    # 判斷已經抓過上個月的資料，則略過不抓

    all_codes = []
    ttype = ["tse", "otc"]
    reslut = None
    try:
        today = datetime.date.today()
        with dbinst.getsession()() as session:
            reslut = session.query(stockinfo).filter(stockinfo.type.in_(ttype)).all()

            for data in reslut:
                # print(data.stockcode)
                all_codes.append(data.stockcode)
                # mySymbols.append(data.stockcode)
            # all_codes = {x.stockcode : x for x in reslut}
            # {x.stockcode: x for x in StockAfters}
    except Exception as e:
        print(f"資料處理錯誤: {e}")

    iIndex = 0
    for code in all_codes:
        iIndex = iIndex + 1
        print(f"[{iIndex}/{len(all_codes)}]-{code}")
        get_monthly_revenue(code)
        time.sleep(2)
    # print(all_codes)
    # all_data = []

    # for _, row in tqdm(all_codes.iterrows(), total=len(all_codes)):
    #     code = row["code"]
    #     df = get_monthly_revenue(code, year, month)
    #     if df is not None:
    #         all_data.append(df)
    #     time.sleep(0.2)  # 避免對伺服器造成壓力

    # if all_data:
    #     final_df = pd.concat(all_data, ignore_index=True)
    #     filename = f"TWSE_Revenue_{year}_{str(month).zfill(2)}.xlsx"
    #     final_df.to_excel(filename, index=False, engine="openpyxl")
    #     print(f"\n✅ 已匯出檔案：{filename}")
    # else:
    #     print("⚠️ 未取得任何資料")


# ------------------------------
# 抓取單一公司月營收
# ------------------------------
def get_monthly_revenue(STOCK_ID: str):

    # STOCK_ID = 2330
    headers = {
        "User-Agent": StockLib._get_user_agent(),
        "cookie": "CLIENT%5FID=20251107211058531%5F125%2E229%2E165%2E156; IS_TOUCH_DEVICE=F; SCREEN_SIZE=WIDTH=2560&HEIGHT=1440; _ga=GA1.1.1416884334.1762521061; cto_bundle=l9Mjt185THpUNENtWWVROWpQOUVlcXJLUzRJUVAlMkJPeDhIUXdDWndjZSUyQlNWSENSNSUyRmVoRnZ3bU8wN0phRFJLOTFKYXRJaFZQVnJPenl2cjF4Mkp1ZHlLUDk5ZEZhTjBwckdUUEpBTkJXaGtnS3luM2pwRXlKJTJGNkZDVXJ6OCUyRjlobTI1TGxYNnVadGQ3UG9waUJsJTJCUGFtS2NGMkRjUmFEdGZiZk9pZnFLQVNoSkI2dEZ0bUd6cWJOUmhPJTJGOW1ZZkdRaFdMalZ0MFhDclBXMGtJcE9aOUslMkJ6dDdtdWRJVFklMkZjQTFNUjE3Q3lDWFcyU3o3SXZ3JTJGbmpjUExEd1RValVNSSUyRkxtNSUyQlRQZXpUMDVvTyUyQlRGeW45aUwwTlQxNjF2QjZaclZBZEUlMkJoWGkzeWR4JTJGcmFabFpQVXhkNVJXdTNGaGNWYWtwYw; TW_STOCK_BROWSE_LIST=2330; FCNEC=%5B%5B%22AKsRol9MKHglgbzHFygDzCBu9Wx6Y9k_RgUHQFfKop97HcvCnB7MzSlRCWEiixYDNOEbaCVB8NWYUSSMEhzmKWY30rtSeKzghWkQwy6nNeOgy2r_Fb0je4i6XD_mQ67TSg5PB5IIPA33jRKo8xOkXg3lbsslA1FLOg%3D%3D%22%5D%5D; SESSION%5FVAL=80350824%2E19; _ga_0LP5MLQS7E=GS2.1.s1762525124$o2$g1$t1762525151$j33$l0$h0; FCCDCF=%5Bnull%2Cnull%2Cnull%2Cnull%2Cnull%2Cnull%2C%5B%5B32%2C%22%5B%5C%22bb090558-327f-472b-9ac1-f2b8ec2ff9ee%5C%22%2C%5B1762521060%2C852000000%5D%5D%22%5D%5D%5D",
    }

    try:
        # 月營收
        res = requests.get(
            f"https://goodinfo.tw/tw/ShowSaleMonChart.asp?STOCK_ID={STOCK_ID}",
            headers=headers,
        )
        res.encoding = "utf-8"
        soup = BeautifulSoup(res.text, "lxml")
        data = soup.select_one("#divSaleMonChartDetail")

        dfs = pd.read_html(StringIO(data.prettify()))
        df = dfs[1]
        df.columns = df.columns.get_level_values(2)
        setColumns = [
            "month",
            "p1",
            "p2",
            "p3",
            "p4",
            "p5",
            "p6",
            "RevenueSingalMonthPrice",
            "RevenueSingalMonthRate",
            "RevenueSingalYearhRate",
            "RevenueSum",
            "RevenueSumYearRate",
            "營收  (億)",
            "月增  (%)",
            "年增  (%)",
            "營收  (億)",
            "年增  (%)",
        ]

        df.columns = setColumns

        # 取得特定欄位資料
        subdf = df[
            [
                "month",
                "RevenueSingalMonthPrice",
                "RevenueSingalMonthRate",
                "RevenueSingalYearhRate",
                "RevenueSum",
                "RevenueSumYearRate",
            ]
        ]

        for row in subdf.itertuples():
            # 只取最多6筆資料
            if row.Index > 12:
                break

            # 調整資料避免資料庫異常
            row.RevenueSingalMonthPrice = (
                row.RevenueSingalMonthPrice if row.RevenueSingalMonthPrice == "-" else 0
            )
            row.RevenueSingalMonthRate = (
                row.RevenueSingalMonthRate if row.RevenueSingalMonthRate == "-" else 0
            )
            row.RevenueSingalYearhRate = (
                row.RevenueSingalYearhRate if row.RevenueSingalYearhRate == "-" else 0
            )
            row.RevenueSum = row.RevenueSum if row.RevenueSum == "-" else 0
            row.RevenueSumYearRate = (
                row.RevenueSumYearRate if row.RevenueSumYearRate == "-" else 0
            )

            with dbinst.getsession()() as session:
                # 寫入資料庫
                DataTemp = (
                    session.query(StockRevenueMonth)
                    .filter(
                        StockRevenueMonth.stockcode == STOCK_ID,
                        StockRevenueMonth.stockdate == row.month,
                    )
                    .first()
                )
                if DataTemp == None:
                    DataTemp = StockRevenueMonth()
                    DataTemp.stockcode = STOCK_ID
                    DataTemp.stockdate = row.month
                    DataTemp.RevenueSingalMonthPrice = row.RevenueSingalMonthPrice
                    DataTemp.RevenueSingalMonthRate = row.RevenueSingalMonthRate
                    DataTemp.RevenueSingalYearhRate = row.RevenueSingalYearhRate
                    DataTemp.RevenueSum = row.RevenueSum
                    DataTemp.RevenueSumYearRate = row.RevenueSumYearRate
                    DataTemp.updatetime = StockLib.getNowDatetime()
                    session.add(DataTemp)

                else:
                    DataTemp.updatetime = StockLib.getNowDatetime()

                session.commit()
            print(
                f"[月營收]{StockLib.getNowDatetime()}-({STOCK_ID})年月:{row.month},抓取寫入完成"
            )

    except Exception as e:
        print(f"資料處理錯誤: {e}")


# ------------------------------
# 程式進入點
# ------------------------------
if __name__ == "__main__":
    # 抓取上市櫃月營收資料
    crawl_all_revenue()
