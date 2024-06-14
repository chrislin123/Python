# from IPython.core.display import HTML
from pyquery import PyQuery as pq
import pandas as pd

TWSE_URL = 'http://isin.twse.com.tw/isin/C_public.jsp?strMode=2'
TPEX_URL = 'http://isin.twse.com.tw/isin/C_public.jsp?strMode=4'

columns = ['dtype', 'code', 'name', '國際證券辨識號碼', '上市日', '市場別', '產業別', 'CFI']

items = []
for url in [TWSE_URL, TPEX_URL]:
    response_dom = pq(url)
    for tr in response_dom('.h4 tr:eq(0)').next_all().items():
        if tr('b'):
            dtype = tr.text()
        else:
            row = [td.text() for td in tr('td').items()]
            code, name = row[0].split('\u3000')
            items.append(dict(zip(columns, [dtype, code, name, *row[1: -1]])))

data = pd.DataFrame(items)

# HTML(data.head().to_html())






