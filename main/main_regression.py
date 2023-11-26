# 重回帰分析の切片を算出し、datasディレクトリに格納する。
# カテゴリ変数は、ダミー変数化するため、カテゴリ変数と非カテゴリ変数で出力ファイルを分割
# Typeは分けて作成する

import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import datetime as dt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error

### パラメータ
# ファイル関係
target_file_dir = "../datas/"
target_file_names = [
    "RealEstateData_20111_20164_13_main",
    "RealEstateData_20171_20234_13_main",
    "RealEstateData_20111_20234_14_main"
]
target_file_end = ".csv"
output_file_suffix = "" #出力ファイルに通し番号や区別をつける場合
output_file_dir = "../datas/"
output_file_end = ".csv"

TradePriceThrethold = 15000
AgeAtTradeThrethold = 50
select_type = "宅地(土地と建物)" #宅地(土地と建物) 中古マンション等
use_cols_noncategory = ["TradePrice","Area","TradeYear","AgeAtTrade"]
category_cols = ['Municipality']
use_cols = use_cols_noncategory + category_cols
AreaThrethold = 300 if select_type == "宅地(土地と建物)" else 100 if select_type == "中古マンション等" else 0

### データの読み込み
df_origin = pd.DataFrame()
for file_name in target_file_names:
    df = pd.read_csv(target_file_dir + file_name + target_file_end)
    df_origin = pd.concat([df_origin, df], axis=0)

### データ整形
col_choice_extract = (~df_origin.AgeAtTrade.isnull())&(df_origin.Type==select_type)
col_choice_threthold = (df_origin.TradePrice<TradePriceThrethold)&(df_origin.Area<AreaThrethold)&(df_origin.AgeAtTrade<AgeAtTradeThrethold)
df_base = df_origin.loc[col_choice_extract&col_choice_threthold,use_cols].copy()
print(df_origin.shape[0], df_origin.loc[col_choice_extract,:].shape[0],df_base.shape[0])

# Prefecture列をOne-Hotエンコーディングして新しい列を作成
df = df_base.copy()
category_col_counts = []
for category_col in category_cols:
    df = pd.get_dummies(df, columns=[category_col])
    df.columns = df.columns.str.split('_').str[-1] #prefixを除去
    category_col_counts.append(len(df_base[category_col].unique()))

### 重回帰分析
# 被説明変数と説明変数に分割
X = df.drop('TradePrice', axis=1)
y = df['TradePrice']

# データの正規化
scaler = StandardScaler()
X_normalized = scaler.fit_transform(X)
X_normalized=X

# 訓練データとテストデータに分割
X_train, X_test, y_train, y_test = train_test_split(X_normalized, y, test_size=0.2, random_state=42)

# 重回帰分析モデルの構築
model = LinearRegression()
model.fit(X_train, y_train)

# モデルの評価（絶対値誤差）
y_pred = model.predict(X_test)
mae = mean_absolute_error(y_test, y_pred)

# 係数と切片の表示
coefficients = dict(zip(X.columns, model.coef_))
intercept = model.intercept_

print('Coefficients:', coefficients)
print('Intercept:', intercept)

# MAEの表示
print('Mean Absolute Error:', mae)


### データの保存
# 説明変数とその切片の値を、記録
# categoryをdummy化したものと、そうでないものでdfを分ける。
df_coef = pd.DataFrame(
    [X.columns, model.coef_],
    index=['col_name', 'coef']
    ).T
df_coef['Type'] = select_type

start_category_col = len(use_cols_noncategory)-1
df_coef_noncate = df_coef.iloc[:start_category_col,:].copy()
df_coef_noncate = df_coef_noncate.loc[:,['Type', 'col_name', 'coef']]


df_coef_cate = df_coef.iloc[start_category_col:,:].copy()

df_coef_cate['col_name_value'] = df_coef_cate.col_name
now_col = 0
for i, category_col in enumerate(category_cols):
    next_col = now_col + category_col_counts[i] 
    df_coef_cate.iloc[now_col:next_col,0]= category_col
    now_col = next_col
df_coef_cate = df_coef_cate.loc[:,['Type','col_name_value', 'col_name', 'coef']]
df_coef_cate

df_coef_noncate.to_csv(output_file_dir + 'RealEsateData_重回帰切片_noncate_' + select_type + output_file_suffix + output_file_end, index=False)
df_coef_cate.to_csv(output_file_dir + 'RealEsateData_重回帰切片_cate_' + select_type + output_file_suffix + output_file_end, index=False)