import yfinance as yf
import pandas as pd
import datetime
import requests
import io
import os
import matplotlib.pyplot as plt
import mplcursors
import ProjectLib

from mail import SendGmailWithImage
from StockLib import getenv

# Logger
from logger import WriteLogTxt

log_obj = WriteLogTxt(
    r"\logs\CalculateMarketBreadthSP500", "LogData", ProjectLib.getLoggerMailSetting()
)
log_obj.setup_logger()

# 設置中文字型與樣式
plt.rcParams["font.sans-serif"] = ["Microsoft JhengHei"]
plt.rcParams["axes.unicode_minus"] = False
plt.style.use("ggplot")

LOCAL_DIR = r"localdata\CalculateMarketBreadthSP500"
TICKER_CACHE = os.path.join(LOCAL_DIR, "sp500_tickers.pkl")
PRICE_CACHE = os.path.join(LOCAL_DIR, "sp500_price_data.pkl")
SENT_LOG = os.path.join(LOCAL_DIR, "sp500_email_sent_log.txt")  # 避免重複發信的紀錄


def get_sp500_tickers():
    now = datetime.datetime.now()
    if os.path.exists(TICKER_CACHE):
        file_time = datetime.datetime.fromtimestamp(os.path.getmtime(TICKER_CACHE))
        if (now - file_time).days < 7:
            return pd.read_pickle(TICKER_CACHE)

    print("🌐 從 Wikipedia 更新 S&P 500 成分股清單...")
    url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    df = pd.read_html(io.StringIO(response.text))[0]
    tickers = [str(t).replace(".", "-") for t in df["Symbol"]]
    pd.to_pickle(tickers, TICKER_CACHE)
    return tickers


def get_price_data(tickers):
    now = datetime.datetime.now()
    start_date = now - datetime.timedelta(days=365 * 10)  # 10 年資料

    if os.path.exists(PRICE_CACHE):
        file_time = datetime.datetime.fromtimestamp(os.path.getmtime(PRICE_CACHE))
        if file_time.date() == now.date():
            print("📦 使用今日 10 年歷史快取...")
            return pd.read_pickle(PRICE_CACHE)

    print(f"🚀 正在同步 10 年歷史數據 (目標: {len(tickers)} 隻)...")
    all_data = yf.download(
        tickers, start=start_date, end=now, auto_adjust=True, threads=True
    )
    all_data.to_pickle(PRICE_CACHE)
    return all_data


def check_and_send_alert(current_val, date):
    """檢查條件並調用您的 SendGmail"""
    if current_val <= 100.0:
        # 檢查紀錄檔，確保一天只發一封
        if os.path.exists(SENT_LOG):
            with open(SENT_LOG, "r") as f:
                if f.read().strip() == str(date):
                    print("📩 今日已發送過通知，不再重複寄送。")
                    return

        print(f"🚨 觸發報警！廣度為 {current_val:.1f}%，正在發送郵件...")

        title = f"🔥 美股市場廣度警報：{current_val:.1f}% (極度超賣)"
        content = f"""
        S&P 500 市場廣度監控報告
        日期：{date}

        當前高於 50 日線比例：{current_val:.2f}%

        目前的數值已跌破 20% 的極度超賣區間。
        這通常發生在市場修正的末端，請檢視您的 Charles Schwab 帳戶進行佈局。
        """

        # 調用您的 mail.py 函式 (請確保收件地址正確)
        # SendGmailWithImage(getenv("MAILTO"), title, content, REPORT_IMG)
        # SendGmail(getenv("MAILTO"), title, content)

        # 寫入發送紀錄
        with open(SENT_LOG, "w") as f:
            f.write(str(date))
    else:
        print(f"✅ 目前市場廣度為 {current_val:.1f}%，尚無需發送通知。")


def get_sp500_oversold_picks(raw_data, sma50, sma200):
    """篩選超跌績優股清單"""
    latest_price = raw_data.iloc[-1]
    latest_sma50 = sma50.iloc[-1]
    latest_sma200 = sma200.iloc[-1]

    # 計算負乖離率 (股價比 50日線 低了多少 %)
    bias_50 = ((latest_price - latest_sma50) / latest_sma50) * 100

    # 篩選條件：1.股價在50日線下 2.股價仍在200日線上(長多)
    # 這裡我們挑選負乖離最大的前 10 名
    oversold_filter = (latest_price < latest_sma50) & (latest_price > latest_sma200)
    top_oversold = bias_50[oversold_filter].sort_values().head(10)

    return top_oversold


def run_breadth_analysis():
    if not os.path.exists(LOCAL_DIR):
        os.makedirs(LOCAL_DIR)

    # 1. 取得數據
    tickers = get_sp500_tickers()
    all_data = get_price_data(tickers)
    raw_data = all_data["Close"] if "Close" in all_data.columns else all_data

    # 2. 計算廣度
    sma50 = raw_data.rolling(window=50).mean()
    daily_breadth = (
        (raw_data > sma50).sum(axis=1) / raw_data.notnull().sum(axis=1)
    ) * 100
    daily_breadth = daily_breadth.dropna()

    current_val = daily_breadth.iloc[-1]
    current_date = daily_breadth.index[-1].date()

    # 3. 呼叫發信檢查 (整合點)
    # check_and_send_alert(current_val, current_date)

    # 4. 指數對照與繪圖
    sp500_idx = yf.download(
        "^GSPC",
        start=daily_breadth.index[0],
        end=datetime.datetime.now(),
        auto_adjust=True,
    )["Close"]
    hist_min = daily_breadth.min()

    fig, (ax1, ax2) = plt.subplots(
        2, 1, figsize=(15, 12), sharex=True, gridspec_kw={"height_ratios": [2, 1]}
    )

    (line1,) = ax1.plot(
        sp500_idx.index, sp500_idx, color="#2980b9", alpha=0.8, label="S&P 500 Index"
    )
    ax1.set_title(
        "S&P 500 指數 vs. 10 年市場廣度 (含自動郵件通知)",
        fontsize=18,
        fontweight="bold",
    )
    ax1.set_ylabel("指數點數")

    (line2,) = ax2.plot(
        daily_breadth.index,
        daily_breadth,
        color="#c0392b",
        linewidth=1,
        label="高於 50 日線比例 (%)",
    )
    ax2.axhline(y=20, color="orange", linestyle="--", label="超賣警戒 (20%)")
    ax2.axhline(
        y=hist_min,
        color="purple",
        linestyle="-",
        linewidth=2,
        label=f"10年歷史最低 ({hist_min:.1f}%)",
    )
    ax2.fill_between(
        daily_breadth.index,
        0,
        daily_breadth,
        where=(daily_breadth <= 20),
        color="darkgreen",
        alpha=0.2,
    )
    ax2.set_ylim(0, 100)
    ax2.legend(loc="upper left", ncol=2)

    # 互動游標
    cursor1 = mplcursors.cursor(line1, hover=True)
    cursor2 = mplcursors.cursor(line2, hover=True)

    @cursor1.connect("add")
    def _(sel):
        date = sp500_idx.index[int(sel.index)].strftime("%Y-%m-%d")
        sel.annotation.set_text(f"日期: {date}\n指數: {sel.target[1]:.2f}")

    @cursor2.connect("add")
    def _(sel):
        date = daily_breadth.index[int(sel.index)].strftime("%Y-%m-%d")
        sel.annotation.set_text(f"日期: {date}\n廣度: {sel.target[1]:.1f}%")

    # --- 關鍵：存檔並檢查發信條件 ---
    REPORT_IMG = os.path.join(LOCAL_DIR, "daily_report.png")
    plt.savefig(REPORT_IMG)  # 1. 先將圖表存成圖片檔

    # 1. 執行超跌選股
    sma200 = raw_data.rolling(window=200).mean()
    oversold_list = get_sp500_oversold_picks(raw_data, sma50, sma200)

    if current_val <= 80.0:
        # 檢查紀錄檔避免重複發信
        if not (
            os.path.exists(SENT_LOG)
            and open(SENT_LOG, "r").read().strip() == str(current_date)
        ):
            # 將清單轉為 HTML 表格
            stock_table = (
                "<table border='1'><tr><th>代碼</th><th>負乖離率 (%)</th></tr>"
            )
            for ticker, bias in oversold_list.items():
                stock_table += f"<tr><td>{ticker}</td><td>{bias:.2f}%</td></tr>"
            stock_table += "</table>"

            print(f"🚨 觸發報警！目前廣度 {current_val:.1f}%，正在發送圖表郵件...")

            title = f"🔥 [美股市場監控]美股市場S&P 500廣度警報：{current_val:.1f}% (極度超賣)={current_date}"
            content = f"""
            S&P 500 市場廣度監控報告
            日期：{current_date}

            當前高於 50 日線比例：{current_val:.2f}%

            目前的數值已跌破 20% 的極度超賣區間。
            這通常發生在市場修正的末端，請檢視您的 Charles Schwab 帳戶進行佈局。
            """
            body = f"""
            <h3>📊 S&P 500 市場廣度深度診斷報告</h3>
            <p><b>當前數值：{current_val:.2f}%</b> (低於 20% 門檻)</p>
            <hr>

            <h4>📌 如何使用這張「市場情緒過濾器」？</h4>
            <ul>
                <li><b>🔴 進入抄底時機：</b> 目前紅色廣度曲線已進入 20% 以下陰影區。這對應歷史上 S&P 500 發生顯著修正（Correction）的末端時刻，代表市場多數股票已跌深，恐慌情緒正處於高點。</li>
                <li><b>🔍 關鍵背離觀察：</b> 請對照圖中<b>藍色指數線</b>與<b>紅色廣度線</b>：
                    <ul>
                        <li>若指數還在跌、廣度線卻悄悄往上走，這就是<b>「底背離」</b>。代表主力資金已開始進場接盤，市場殺盤即將結束。</li>
                        <li>若指數與廣度同步創新低，代表賣壓尚未平息，即便在超賣區仍不宜一次梭哈。</li>
                    </ul>
                </li>
            </ul>

            <h4>💡 2026 年當前投資策略建議</h4>
            <table border="1" cellpadding="10" style="border-collapse: collapse; width: 100%;">
                <tr style="background-color: #f8f9fa;">
                    <th>技術訊號</th>
                    <th>操作行動</th>
                </tr>
                <tr>
                    <td><b>發現「底背離」</b></td>
                    <td><b>積極佈局：</b> 可更自信地在 Charles Schwab 帳戶投入第 2、3 筆資金，優先考慮高 Beta 股（如大型科技股）。</td>
                </tr>
                <tr>
                    <td><b>同步創新低</b></td>
                    <td><b>防禦性佈局：</b> 雖已進入超賣區，但應維持「分批」小量分段佈局，保留現金空間。</td>
                </tr>
            </table>

            <h4>🎯 建議關注之超跌績優標的 (符合長多短空條件)：</h4>
            {stock_table}
            <p>操作策略：建議在 <b>Charles Schwab</b> 帳戶針對上述標的進行分批佈局。</p>

            <p><i>※ 請參考附件圖表進行精確定位。</i></p>
            """

            # 2. 調用新的發信函式，帶入圖片路徑
            SendGmailWithImage(getenv("MAILTO"), title, body, REPORT_IMG)

            with open(SENT_LOG, "w") as f:
                f.write(str(current_date))
        else:
            print(f"✅ 目前市場廣度為 {current_val:.1f}%，尚無需發送通知。")

    plt.tight_layout()
    # 背景執行不用顯示
    # plt.show()
    log_obj.write_log_info(f"美股市場S&P 500廣度警報=={current_date}")


if __name__ == "__main__":
    try:
        run_breadth_analysis()

    except Exception as e:
        log_obj.write_log_exception(
            f"異常內容：{e}",
            f"發生異常: {type(e).__name__}",
        )
