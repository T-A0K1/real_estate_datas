import funcs.etl as etl
import funcs.getData as getData
import numpy as np
import pandas as pd
import datetime as dt

url = "https://www.land.mlit.go.jp/webland/api/TradeListSearch"

# 取得データのパラメータ設定
save_dir = "../datas/"
## 
# areas = ['01', '08','28', '27', '35', '40']
areas = ['01', '08','28' ]
from_and_to = ['20111', '20234']
parameters = [
    {"from": from_and_to[0],
     "to": from_and_to[1],
     "area":area
     }
    for area in areas
    ]

# 各種前処理のパラメータ
drop_cols = ['PricePerUnit', 
            #  'Purpose', 
             'Direction', 'Classification']

# val: m2が含まれる値を、何に置換するか
needRemoveVal = [
    ['Frontage','m以上','over'], 
    ['Area','㎡以上','over'],
    ['Area','m&sup2;以上','over'],
    ['Area',',','over'],
    ['TotalFloorArea', '㎡以上','over'],
    ['TotalFloorArea', 'm^2未満','under'],
    ['TotalFloorArea', 'm&sup2;以上','over']
]
changeDataTypeVal = {
    'TradePrice':'Int64',
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
# データ取得
df = pd.DataFrame()
for param in parameters:
    print(dt.datetime.now())
    df_tmp = getData.getData(url, param)
    df_tmp['PrefectureNo'] = param['area']
    df = pd.concat([df, df_tmp]).reset_index(drop=True)

# 不要列の削除
df2 = df.drop(drop_cols, axis=1)

df2.to_csv('../datas/debug_data.csv', index=False)

# 数値列を数値に変換
df2 = etl.RemoveM2(df2, needRemoveVal)
df2 = etl.changeDataType(df2, changeDataTypeVal)

# 行の抽出(非住宅の除去など)
print(df2.shape)
df2 = etl.extractRow(df2, extractCondionDic)
print(df2.shape)

# 時系列値の整形
df2 = etl.changeCalendarBuildingYear(df2)
df2 = etl.spritPeriodTradeYearQuarter(df2)
df2 = etl.makeYearOldatTrade(df2)

# 数値データのカテゴリ化
for key, values in addClassOfNonCategoryDataDic.items():
    df2 = etl.add_class_of_noncategory_data(
        df2, 
        target_col_=key, 
        bins_=values)
    
# データのtradeNo(ユニークな連番)を追加
df2 = etl.add_tradeno(df2)

# priceを万円に
df2['TradePrice'] = df2.TradePrice/10000

# FloorPlan列を整理
df2 = etl.replace_floor_plan(df2)

# メインの分析対象の列とそうでない列を分割
df2_main, df2_sub = etl.split_main_sub(df2, main_cols)

# 集合住宅のTotalFlooraAreaに集合住宅のAreaを挿入
df2_main = etl.copy_area_to_total_floor_area(df2_main)

# TotalFloorAreaがnullのデータを除去(おそらく建物が建ってない)
df2_main = df2_main[~df2_main.TotalFloorArea.isnull()].copy()

# ファイルの保存
file_name_main, file_name_sub = etl.make_save_file_name(areas, from_and_to, save_dir)

df2_main.to_csv(file_name_main, index=False)
df2_sub.to_csv(file_name_sub, index=False)
