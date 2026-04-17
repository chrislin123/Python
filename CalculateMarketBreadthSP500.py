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
from logger import get_logger

log_obj = get_logger()

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
    # 在 ax2 的繪圖邏輯中加入
    ax2.axhline(y=80, color="green", linestyle="--", label="超買警戒 (80%)")
    # 填充超漲區 (80% 以上使用淺綠色或淺紅色)
    ax2.fill_between(
        daily_breadth.index,
        80,
        100,
        where=(daily_breadth >= 80),
        color="lightcoral",  # 使用淺紅色代表高風險區
        alpha=0.3,
        label="超漲獲利區",
    )
    # ax2.axhline(
    #     y=hist_min,
    #     color="purple",
    #     linestyle="-",
    #     linewidth=2,
    #     label=f"10年歷史最低 ({hist_min:.1f}%)",
    # )
    ax2.fill_between(
        daily_breadth.index,
        0,
        daily_breadth,
        where=(daily_breadth <= 20),
        color="darkgreen",
        alpha=0.2,
        label="超跌恐慌區",
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

    # if current_val <= 80.0:
    # 檢查紀錄檔避免重複發信
    if not (
        os.path.exists(SENT_LOG)
        and open(SENT_LOG, "r").read().strip() == str(current_date)
    ):
        # 將清單轉為 HTML 表格
        stock_table = "<table border='1'><tr><th>代碼</th><th>負乖離率 (%)</th></tr>"
        for ticker, bias in oversold_list.items():
            stock_table += f"<tr><td>{ticker}</td><td>{bias:.2f}%</td></tr>"
        stock_table += "</table>"

        print(f"🚨 觸發報警！目前廣度 {current_val:.1f}%，正在發送圖表郵件...")

        current_status = ""
        # 1. 定義市場情緒判斷邏輯
        if current_val > 80:
            current_status = "極度亢奮 / 超漲"
            alert_emoji = "⚠️"
        elif 70 < current_val <= 80:
            current_status = "偏向樂觀"
            alert_emoji = "📈"
        elif 30 <= current_val <= 70:
            current_status = "常態區間"
            alert_emoji = "⚖️"
        elif 20 <= current_val < 30:
            current_status = "偏向恐慌"
            alert_emoji = "🔍"
        else:  # current_val < 20
            current_status = "極度恐慌 / 超跌"
            alert_emoji = "🔥"

        # 根據比例給予操作建議
        action_advice = ""
        if current_val > 80:
            action_advice = (
                "建議策略：<b>分批獲利了結</b>。市場已過熱，嚴禁在此時追高加碼。"
            )
        elif current_val < 20:
            action_advice = "建議策略：<b>分批加碼佈局</b>。尋找「底背離」買點，分批投入 Charles Schwab 帳戶。"
        else:
            action_advice = "建議策略：依照個股趨勢操作，維持現有持股部位。"

        title = f"{alert_emoji} [美股市場監控]美股市場S&P 500廣度警報：{current_val:.1f}% ({current_status})={current_date}"

        body = f"""
        <h3>📊 S&P 500 市場廣度深度診斷報告</h3>
        <p><b>當前數值：{current_val:.2f}%</b> </p>
        <hr>

        <h4>💡 當前投資操作建議</h4>

        <p style="color: #FF0000; font-weight: bold; font-size: 1.1em;">{action_advice}</p>
        <p><i>※ 請查閱附件圖表觀察是否有「頂背離」或「底背離」跡象。</i></p>

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
        <ul>
            <li><b>🔴 進入獲利時機：</b> 目前紅色廣度曲線已進入 80% 以上陰影區。這對應歷史上 S&P 500 發生顯著上漲（Correction）的末端時刻，代表市場多數股票已漲多，樂觀情緒正處於高點。</li>
            <li><b>🔍 關鍵背離觀察：</b> 請對照圖中<b>藍色指數線</b>與<b>紅色廣度線</b>：
                <ul>
                    <li>若指數還在漲、廣度線卻悄悄往下走，這就是<b>「頂背離」</b>。代表主力資金已開始退場賣盤，市場漲勢即將結束。</li>
                    <li>若指數與廣度同步創新高，代表買盤尚未平息，即便在超買區仍不宜一次出清。</li>
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
        <table border="1" cellpadding="10" style="border-collapse: collapse; width: 100%;">
            <tr style="background-color: #f8f9fa;">
                <th>技術訊號</th>
                <th>操作行動</th>
            </tr>
            <tr>
                <td><b>頂背離（Bearish Divergence）：最重要的逃頂訊號</b></td>
                <td><b>這不是「買入」的好時機，反而是應該在 Charles Schwab 帳戶中分批獲利了結，或調緊移動停損點的時刻</td>
            </tr>
            <tr>
                <td><b>這代表支撐指數上漲的力量正在縮小，資金集中在少數幾檔大型權值股（如科技七巨頭），大多數的中小型股票已經開始偷偷回落</b></td>
                <td><b>防禦性佈局：</b> 雖已進入超賣區，但應維持「分批」小量分段佈局，保留現金空間。</td>
            </tr>
            <tr>
                <td><b>70% - 80%：超買警戒區</b></td>
                <td><b>當比例超過 70%，代表市場大多數股票都已經歷了一段顯著漲幅，短線回擋的機率開始上升。</td>
            </tr>
            <tr>
                <td><b>80% 以上：極度超漲區（歷史極值）</b></td>
                <td><b>根據歷史紀錄，當比例達到 80% 至 90% 之間，通常意味著市場情緒已達到「亢奮（Euphoria）」狀態。這時市場幾乎沒有人想賣出，但潛在買盤也已消耗殆盡，往往是中長期「頂部」或「重大修正」的前兆。</td>
            </tr>
        </table>

        <h4>💡 總結操作策略表</h4>
        <table border="1" cellpadding="10" style="border-collapse: collapse; width: 100%;">
            <tr style="background-color: #f8f9fa;">
                <th>市場廣度比例</th>
                <th>市場情緒</th>
                <th>建議行動 (Charles Schwab)</th>
            </tr>
            <tr>
                <td><b>80%</b></td>
                <td>極度亢奮 / 超漲</td>
                <td>分批獲利了結，嚴禁追高。</td>
            </tr>
            <tr>
                <td><b>70% - 80%</b></td>
                <td>偏向樂觀</td>
                <td>觀察是否有頂背離，調緊停損。</td>
            </tr>
            <tr>
                <td><b>30% - 70%</b></td>
                <td>常態區間</td>
                <td>持股續抱，依個股趨勢操作。</td>
            </tr>
            <tr>
                <td><b>20% - 30%</b></td>
                <td>偏向恐慌</td>
                <td>開始留意超跌標的。</td>
            </tr>
            <tr>
                <td><b>< 20%</b></td>
                <td>極度恐慌 / 超跌</td>
                <td>分批加碼，尋找底背離買點。</td>
            </tr>
        </table>

        <h4>🎯 建議關注之超跌績優標的 (符合長多短空條件)：</h4>
        {stock_table}


        <p><i>※ 請參考附件圖表進行精確定位。</i></p>
        """

        # 2. 調用新的發信函式，帶入圖片路徑
        SendGmailWithImage(getenv("MAILTO"), title, body, REPORT_IMG)

        with open(SENT_LOG, "w") as f:
            f.write(str(current_date))
        # else:
        #     print(f"✅ 目前市場廣度為 {current_val:.1f}%，尚無需發送通知。")

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
