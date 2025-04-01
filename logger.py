import logging.handlers
import os
import logging
from datetime import datetime

class WriteLogTxt:
    '''
    setup_logger  設置logging格式及創立文件夾
    write_log_info 指定檔案名稱及log內容輸入
    write_log_warning
    '''
    def __init__(self,file_path,file_name):
        self.file_path = file_path
        self.file_name = file_name

    def setup_logger(self):
        '''
        設置logging格式及創立文件夾
        '''
        now = datetime.now()
        year_month = now.strftime("%Y-%m") #取得字符串
        if self.file_path == '': #如果都沒填寫，從根目錄建立
            log_folder = os.path.join(os.getcwd(), year_month)
        else:
            if self.file_path[0:1] == '\\': #有填相對路徑，則從根目錄開始
                fomatfile_path = self.file_path.replace('\\','',1)
                log_folder = os.path.join(os.getcwd(), fomatfile_path, year_month)
            else: #直接指定Log路徑
                log_folder = os.path.join(self.file_path, year_month)
        # 檢查文件夾與文件是否存在
        if not os.path.exists(log_folder):
            os.makedirs(log_folder)
         # 設置格式
        log_format = "%(asctime)s - %(levelname)s - %(message)s" # 日期時間 日誌的等級名稱 訊息
        # file_handler = logging.FileHandler(os.path.join(log_folder, f"{self.file_name}_{now.date()}.log"))
        # file_handler = logging.handlers.TimedRotatingFileHandler(os.path.join(log_folder, f"{self.file_name}_{now.date()}.log")
        #                                                          ,'M',1,0)
        #每十分鐘產生一個檔案
        file_handler = logging.handlers.TimedRotatingFileHandler(os.path.join(log_folder, f"{self.file_name}")
                                                                 ,'M',10,0)
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter(log_format))

        # 設置logger
        self.logger = logging.getLogger(self.file_name)
        self.logger.setLevel(logging.INFO)
        self.logger.addHandler(file_handler)

    # 指定檔案名稱及log內容輸入
    def write_log_info(self,log_content):
        '''
        log_content : Log
        '''
         # 寫入log
        self.logger.info(f"{log_content}")

    def write_log_warning(self,log_content):
        '''
        log_content : Log
        '''
         # 寫入log
        self.logger.warning(f"{log_content}")
