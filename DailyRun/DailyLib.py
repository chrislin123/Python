
import os
from datetime import datetime
import requests
import pandas as pd

#讀取機敏設定檔
from dotenv import get_key,load_dotenv

def getenv(getenv):
    load_dotenv()
    return os.getenv(getenv)



def getPrefixFile_raw(targetDir,prefix):

    #找到關鍵字開頭的檔案，回傳陣列
    fs = [os.path.join(targetDir, f) for f in os.listdir(targetDir) if f.lower().startswith(f"{prefix}")]

    return fs




