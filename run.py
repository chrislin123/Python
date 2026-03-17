import datetime
import random
import time
import ProjectLib


from logger import WriteLogTxt

log_obj = WriteLogTxt(r"\logs\TaskLog", "TaskLog", ProjectLib.getLoggerMailSetting())
log_obj.setup_logger()


log_obj.write_log_info("test")

try:
    # 執行轉檔邏輯...
    # 你想要嘗試執行的程式碼
    print(10 / 0)

except Exception as e:
    log_obj.write_log_exception(
        f"異常內容：{e}",
        f"發生異常: {type(e).__name__}",
        # mail_subject=f"致命錯誤 - NPSlumpXML 伺服器: {os.environ.get('COMPUTERNAME')}",
    )


# LineLib
# from LineLib import PushMessageEarn2


# PushMessageEarn2('test')


# for i in range(100):
#     print(datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S"))
#     #randint = random.randint(5,10)
#     #間隔三秒
#     #print('間隔{0}秒'.format(randint))
#     time.sleep(1)


# tpcc ymgw mmtm avlp
