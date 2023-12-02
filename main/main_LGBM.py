# LGBMでモデルを作成し、指定した説明変数の組み合わせで予測結果を出力しファイルに保存する

import pandas as pd
import numpy as np
import datetime as dt
import lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error

import datetime as dt
start_time = dt.datetime.now()

### パラメータ
# ファイル関係
target_file_dir = "../datas/"
target_file_names = [
    "RealEstateData_20121_20154_14_13_main",
    "RealEstateData_20161_20194_14_13_main",
    "RealEstateData_20201_20234_14_13_main"
]
target_file_end = ".csv"
output_file_suffix = "_20231126" #出力ファイルに通し番号や区別をつける場合
output_file_dir = "../datas/"
output_file_end = ".csv"

# 
TradePriceThrethold = 15000
AgeAtTradeThrethold = 50
AreaThrethold = 200
use_cols_non_cate = ["TradePrice","Area","TradeYear","AgeAtTrade", 'TotalFloorArea', 'CoverageRatio', "FloorAreaRatio"]
category_cols = ['Municipality', 'Structure' ,'Type']
use_cols = use_cols_non_cate + category_cols

# LGBM用パラメータの設定
params = {
    'objective': 'regression',
    'metric': 'mae',
    'boosting_type': 'gbdt',
    'num_leaves': 63,
    'learning_rate': 0.03,
    'bagging_freq': 1, 
    'feature_fraction': 0.9
}
verbose_eval = 1

### データ読み込み
df_origin = pd.DataFrame()
for file_name in target_file_names:
    df = pd.read_csv(target_file_dir + file_name + target_file_end)
    df_origin = pd.concat([df_origin, df], axis=0)

col_choice_extract = (~df_origin.AgeAtTrade.isnull())
col_choice_threthold = (df_origin.TradePrice<TradePriceThrethold)&(df_origin.Area<AreaThrethold)&(df_origin.AgeAtTrade<AgeAtTradeThrethold)
df_base = df_origin.loc[col_choice_extract&col_choice_threthold,use_cols].copy()
print(df_origin.shape[0], df_origin.loc[col_choice_extract,:].shape[0],df_base.shape[0])

### データ作成
df = df_base.copy()

#Municipalityを数字に変換
mapping_dict = {}
for category_col in category_cols:
    df[category_col], mapping_dict[category_col] = pd.factorize(df[category_col]) 

# 目的変数と説明変数に分割
y = df['TradePrice']
X = df.drop('TradePrice', axis=1)

# テストデータと学習データ分割
# 参考：https://qiita.com/c60evaporator/items/2b7a2820d575e212bcf4
X_train_raw, X_test, y_train_raw, y_test = train_test_split(X, y, test_size=0.05, random_state=42)
# early_stopping用の評価データをさらに分割
X_train, X_valid, y_train, y_valid = train_test_split(X_train_raw, y_train_raw, test_size=0.2, random_state=42)

###### ここからがLightGBMの実装 ######
# データをDatasetクラスに格納
dtrain = lgb.Dataset(X_train, label=y_train, categorical_feature=category_cols)  # 学習用
dvalid = lgb.Dataset(X_valid, label=y_valid, categorical_feature=category_cols)  # early_stopping用

# LightGBMモデルの訓練
model = lgb.train(params, dtrain, 
                  num_boost_round=10000, 
                  valid_sets=[dvalid], 
                  callbacks=[lgb.early_stopping(stopping_rounds=40, 
                                verbose=True), # early_stopping用コールバック関数
                           lgb.log_evaluation(verbose_eval)])

# モデルの評価（MAE）
y_pred = model.predict(X_test, num_iteration=model.best_iteration)
mae = mean_absolute_error(y_test, y_pred)
print('Mean Absolute Error:', mae)

### 予測用dummyデータの作成
# dummy予測データ作成用パラメータ
from itertools import product

Type_list = ['宅地(土地と建物)']
Area_list = [x for x in range(20,101,10)] + [150,200]
TradeYear_list = [2015,2020,2025]
AgeAtTrade_list = [0,10,20, 30, 40, 50]
Municipality_list = [x for x in df_origin.Municipality.unique()]
Structure_list = ['木造']
TotalFloorArea_list = [x for x in range(50,201,50)] + [np.nan]
CoverageRatio_list = [60]
FloorAreaRatio_list = [100, 200, 300, 500]
#['1K', '1LDK', '1R', '2LDK', '3LDK', '4LDK']

Tyoe_list_2 = ['中古マンション等']
Area_list_2 = [x for x in range(20,101,10)] + [150, 200]
# Municipality_for_m = df_origin.query('Type=="中古マンション等"').pivot_table(index='Municipality', values='Area', aggfunc='count').sort_values('Area').query('Area>20').index
# Municipality_list_2 = [x for x in Municipality_for_m]
TotalFloorArea_list_2 = [np.nan]
FloorAreaRatio_list_2 = [100, 200, 300, 500]
CoverageRatio_list_2 = [80]
Structure_list_2 = ['ＲＣ']

# 各リストの組み合わせを生成
combinations= list(product(Area_list, TradeYear_list, AgeAtTrade_list, Municipality_list, Structure_list, Type_list,
                            TotalFloorArea_list, CoverageRatio_list, FloorAreaRatio_list))

combinations_2= list(product(Area_list_2, TradeYear_list, AgeAtTrade_list, Municipality_list, Structure_list_2, Tyoe_list_2,
                            TotalFloorArea_list_2, CoverageRatio_list_2, FloorAreaRatio_list_2))

# リストからDataFrameを作成
df = pd.DataFrame(combinations, columns=['Area', 'TradeYear', 'AgeAtTrade', 'Municipality', 'Structure', 'Type', 
                                         'TotalFloorArea','CoverageRatio', 'FloorAreaRatio'])
df2 = pd.DataFrame(combinations_2, columns=['Area', 'TradeYear', 'AgeAtTrade', 'Municipality', 'Structure', 'Type', 
                                         'TotalFloorArea','CoverageRatio', 'FloorAreaRatio'])
df_dummy = pd.concat([df,df2]).reset_index(drop=True)
df_dummy_m = df_dummy.loc[:,X_test.columns]
print(df_dummy.shape)

# カテゴリー変数を、モデル作成時の変換マップの値で置換
df_dummy_m = df_dummy.copy()
for category_col in category_cols:
    df_dummy_m[category_col] = df_dummy_m[category_col].map({val: i for i, val in enumerate(mapping_dict[category_col])})

# 予測結果の代入
df_dummy['TradePrice_Predict'] = model.predict(df_dummy_m)

### でーたの保存
df_dummy.to_csv(output_file_dir + 'RealEstateData_LGBM' + output_file_suffix + output_file_end, index=False)

end_time = dt.datetime.now()

print('start:', start_time)
print('end:', end_time)