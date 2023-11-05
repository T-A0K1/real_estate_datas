import funcs.etl as etl
import funcs.getData as getData
import numpy as np
import pandas as pd

url = "https://www.land.mlit.go.jp/webland/api/TradeListSearch"
parameters = {
    "from": "20211",
    "to": "20234",
    "area": "14"
}

drop_cols = ['PricePerUnit', 
            #  'Purpose', 
             'Direction', 'Classification']
# val: m2が含まれる値を、何に置換するか
needRemoveVal = [
    ['Frontage','m以上','over'], 
    ['Area','㎡以上','over'],
    ['TotalFloorArea', '㎡以上','over'],
    ['TotalFloorArea', 'm^2未満','under']
]
changeDataTypeVal = {
    'TradePrice':'int',
    'Frontage':'float',
    'Area':'int',
    'UnitPrice':'float',
    'TotalFloorArea':'float',
    'Breadth':'float',
    'CoverageRatio':'float',
    'FloorAreaRatio':'float'
}
extractCondionDic = {
    'Type':['宅地(土地と建物)', '中古マンション等'],
    'Remarks': 'Nan',
    'Use': ['住宅',  np.nan, '共同住宅', '住宅'],
    'Purpose':['住宅',  np.nan]
    }

df = getData.getData(url, parameters)
df2 = df.drop(drop_cols, axis=1)
df2 = etl.RemoveM2(df2, needRemoveVal)
df2 = etl.changeDataType(df2, changeDataTypeVal)
print(df2.shape)
df2 = etl.extractRow(df2, extractCondionDic)
print(df2.shape)
df2 = etl.changeCalendarBuildingYear(df2)
df2 = etl.spritPeriodTradeYearQuarter(df2)
df2 = etl.makeYearOldatTrade(df2)

file_name = f"RealEstateData_{parameters['from']}_{parameters['to']}_{parameters['area']}.csv"
df2.to_csv('../datas/'+file_name, index=False)



