import funcs.etl as etl
import funcs.getData as getData
import numpy as np
import pandas as pd

url = "https://www.land.mlit.go.jp/webland/api/TradeListSearch"
parameters = {
    "from": "20221",
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

addClassOfNonCategoryDataDic ={
    'TradePrice':[i*1000 for i in range(11)],
    'Area': [0,20,40,60,80,100,120,140,160,180,200],
    'TotalFloorArea':[50,70,80,90,100,150,200],
    'Breadth': [i*2 for i in range(5)],
    'CoverageRatio':[i for i in [0,30,40,50,60,80]],
    'FloorAreaRatio': [i*10 for i in [0,10,15,20,30,40]],
    'AgeAtTrade':  [-2]+[i*5 for i in range(11)]
}

main_cols = [
    'Type','Prefecture', 'Municipality', 'DistrictName',
    'Structure', 'FloorPlan',
    'TradePrice', 'AgeAtTrade','Area',
    'TotalFloorArea','CoverageRatio', 'FloorAreaRatio',
    'BuildingYearW','TradeYear', 'TradeQuarter'
    ]

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
for key, values in addClassOfNonCategoryDataDic.items():
    df2 = etl.add_class_of_noncategory_data(
        df2, 
        target_col_=key, 
        bins_=values)
df2 = etl.add_tradeno(df2)
df2_main, df2_sub = etl.split_main_sub(df2, main_cols)

file_name_main = f"RealEstateData_{parameters['from']}_{parameters['to']}_{parameters['area']}_main.csv"
file_name_sub = f"RealEstateData_{parameters['from']}_{parameters['to']}_{parameters['area']}_sub.csv"

df2_main.to_csv('../datas/'+file_name_main, index=False)
df2_sub.to_csv('../datas/'+file_name_sub, index=False)



