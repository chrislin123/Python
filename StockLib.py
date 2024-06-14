
import os
from datetime import datetime

import pandas as pd




def LogRunTimeToCsv(self , FileFullName):

    # os.path.basename(FileFullName).split('.')[0]

    # 取得現在時間
    # now = datetime.datetime.now()
    txt = '上次更新時間為：' + str(getNowDatetime())

    # 轉成df
    df = pd.DataFrame([txt], index=['UpdateTime'])

    # 存出檔案
    df.to_csv('log_{0}.csv'.format(os.path.basename(FileFullName).split('.')[0]) , header=False)



#回傳Stock專案時間文字格式(2024-05-31T21:07:35)
def getNowDatetime():
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

#回傳Stock專案時間文字格式(20240531)
def getNowDate():
    return datetime.now().strftime("%Y%m%d")



