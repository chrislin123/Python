import json
from json import load


#資料庫連線相關及Orm.Model
from db import dbinst,StockBroker1,StockBrokerBSAmo,StockLog,CityArea

jsonFile = open('D:\專案資料\M15_113\縣市行政區.json','r',encoding="utf-8")
a = json.load(jsonFile)
cityname = ''
areaname = ''
cityarealist = []
for i in a:
    cityname = i['CityName']
    for x in i['AreaList']:
        areaname = x['AreaName']
        # areaname
        print('{0}-{1}'.format(cityname,areaname))
        item = [cityname,areaname,x['ZipCode']]
        cityarealist.append(item)




try:
    with dbinst.getsession()() as session:


        for data in cityarealist:
                print(data)
                # date_time = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

                article = session.query(CityArea).filter(
                        CityArea.CityName == data[0]
                        ,CityArea.AreaName == data[1]
                        ).first()

                if article == None:
                    article = CityArea()
                    article.CityName = data[0]
                    article.AreaName = data[1]
                    article.ZipCode = data[2]
                    session.add(article)
                else:
                    article.CityName = data[0]
                    article.AreaName = data[1]
                    article.ZipCode = data[2]

                session.commit()

except Exception as e:
    print(f"Encounter exception: {e}")


