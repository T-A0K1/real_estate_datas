import pandas as pd
import mojimoji
import numpy as np

def RemoveM2(df_, needRemoveVal:list):
    # 指定列のデータからtarget_wordを除去
    # 新規列を追加し、除去した行はフラグを立てる(基本XX以上を想定して、overという列を新規追加)
    for col, target_word, nwe_col_word in needRemoveVal:
        new_col = f'{col}_{nwe_col_word}_flag'
        target_row = df_.loc[:, col].str.contains(target_word).fillna(False)
        print(col, target_word, sum(target_row))
        df_[new_col] = 0
        df_.loc[target_row, new_col] = 1
        df_[col] = df_.loc[:,col].str.replace(target_word,'')
        
    return df_

def changeDataType(df_,changeDataTypeVal:dict):
    # float及びintへの変換
    for col,new_data_type in changeDataTypeVal.items():
        print(col,new_data_type)
        df_[col] = df_.loc[:,col].astype(new_data_type)
    return df_

def extractRow(df_, extractCondionDic):
    before_len = df_.shape[0]
    # 特定の行の除去
    for col, targetValue in extractCondionDic.items():
        if targetValue =='Nan': # Nanと他のも選びたい場合汎用性ないけど、とりあえず
            df_ = df_[df_[col].isna()]
        else:
            target_row = df_[col].isin(targetValue)
            df_ = df_[target_row]
    after_len = df_.shape[0]
    print(f"before:{before_len}, after:{after_len}")
    return df_

def changeCalendarBuildingYear(df_):
    # 和暦を西暦にする
    
    df_dummy = df_.loc[:,['BuildingYear']].copy()
    df_dummy['Koyomi'] = df_.BuildingYear.str[:2]
    
    df_dummy['KoyomiYear'] = df_dummy.BuildingYear.str[2:].str.replace("年", "")
    df_dummy.loc[df_dummy.KoyomiYear=="", 'KoyomiYear'] = "1900" #上記では戦前が消えてるので
    df_dummy['KoyomiYear'] = df_dummy.KoyomiYear.astype('float')
    
    ### これで、暦と、その年を分けれたはずなので、あとはそれを西暦に直す
    # 昭和+1925,平成+1988, 令和+2018
    df_['BuildingYearW'] = df_dummy['KoyomiYear']
    df_.loc[df_dummy.Koyomi=="戦前", 'BuildingYearW'] = 1900
    df_.loc[df_dummy.Koyomi=="昭和", 'BuildingYearW'] = df_dummy.loc[df_dummy.Koyomi=="昭和", 'KoyomiYear'] + 1925
    df_.loc[df_dummy.Koyomi=="平成", 'BuildingYearW'] = df_dummy.loc[df_dummy.Koyomi=="平成", 'KoyomiYear'] + 1988
    df_.loc[df_dummy.Koyomi=="令和", 'BuildingYearW'] = df_dummy.loc[df_dummy.Koyomi=="令和", 'KoyomiYear'] + 2018
    
    return df_

def spritPeriodTradeYearQuarter(df_):
    # Periodの書式：2022年第２四半期
    df_['TradeYear'] = df_.Period.str[:4].astype('int')
    df_['TradeQuarter'] = df_.Period.str[6].astype('int')
    
    return df_ 

def makeYearOldatTrade(df_):
    df_['AgeAtTrade'] = df_.TradeYear - df_.BuildingYearW
    return df_
    
def add_class_of_noncategory_data(df_, target_col_, bins_):
    # 指定列に対して、指定したbins(左端指定)でのhistgramを作成
    bins_ = bins_ + [999999]

    df_['Classified_'+target_col_+'_int'] = pd.cut(df_[target_col_], bins=bins_, labels=bins_[:-1])
    labels_for_str = [str(bins_[i])+'~'+str(bins_[i+1]) for i in range(len(bins_)-2)]
    labels_for_str = labels_for_str + [str(bins_[-2]) + '~'] #一番大きいラベルは、右端のみ
    df_['Classified_'+target_col_+'_str'] = pd.cut(df_[target_col_], bins=bins_, labels=labels_for_str)
    
    df_['Classified_'+target_col_+'_str'] = df_['Classified_'+target_col_+'_str'].cat.add_categories('Empty').fillna('Empty')
        
    return df_
        
def add_tradeno(df_):
    df_ = df_.sort_values(['Prefecture','MunicipalityCode', 'DistrictName',
                     'BuildingYearW','TradePrice','Area']).copy()
    df_['TradeNo'] = range(len(df_))
    return df_

def split_main_sub(df_, main_cols):
    df2_main = df_.loc[:,['TradeNo']+main_cols].copy()
    df2_sub =  df_.drop(main_cols, axis=1).copy()
    # df2_subの先頭の列をTradeNoにする
    cols = list(df2_sub.columns)
    cols = ['TradeNo'] + [col for col in cols if col != 'TradeNo']
    df2_sub = df2_sub[cols]
    
    return df2_main, df2_sub

def replace_floor_plan(df):
    # FloorPlan列を前処理
    df_ = df.copy()
    # 0. 元のFloorPlan列をFloorPlanOrigin列として残す
    df_['FloorPlanOrigin'] = df_['FloorPlan']

    # 1. "FloorPlanFlagDK(K)"列と"FloorPlanFlagS"列と"FloorPlanNumber"列を作る(デフォルト値は0)
    df_['FloorPlanNumber'] = 0

    # 2. 全角のアルファベットと数字と半角にする
    # 全角に変換する関数
    def to_full_width(text):
        return mojimoji.zen_to_han(text)
    # Nanがあるとダメなので置換
    df_['FloorPlan'] = df_.loc[:,['FloorPlan']].fillna('empty')
    # DataFrameの要素を全角に変換
    df_['FloorPlan'] = df_.loc[:,['FloorPlan']].applymap(to_full_width)

    # 3. "FloorPlanSTR"列を作成する。デフォルト値はFloorPlan列とする。その後、FloorPlanSTR列の先頭の文字が数字の場合、その数字を除去する
    df_['FloorPlanSTR'] = df_['FloorPlan'].astype(str)
    df_['FloorPlanSTR'] = df_['FloorPlan'].astype(str).apply(lambda x: x[1:] if x[0].isdigit() else x)

    # 4. FloorPlan列の先頭の文字が数字の行について、その数字でFloorPlanNumber列を更新する
    df_['FloorPlanNumber'] = np.where(df_['FloorPlan'].astype(str).apply(lambda x: x[0].isdigit()),
                                    df_['FloorPlan'].astype(str).apply(lambda x: x[0]), df_['FloorPlanNumber'])

    # 5. FloorPlan列の先頭の文字が数字の行について、その数字を除いた値でFloorPlanSTR列を更新する
    df_['FloorPlanSTR'] = np.where(df_['FloorPlan'].astype(str).apply(lambda x: x[0].isdigit()),
                                df_['FloorPlan'].astype(str).apply(lambda x: x[1:]), df_['FloorPlanSTR'])
    
    # 6. FloorPlanSTR列が"K"か”DK”かつ、FloorPlanNumber列が1でない行について、FloorPlanNumberを-1して、FloorPlanSTRを"LDK"にする
    df_['FloorPlanNumber'] = np.where(((df_['FloorPlanSTR'] == 'K') | (df_['FloorPlanSTR'] == 'DK')) &
                                      (df_['FloorPlanNumber'] != '1'),
                                      df_['FloorPlanNumber'].astype(int) - 1, df_['FloorPlanNumber'])
    df_['FloorPlanSTR'] = np.where(((df_['FloorPlanSTR'] == 'K') | (df_['FloorPlanSTR'] == 'DK')) &
                                   (df_['FloorPlanNumber'] != '1'), 'LDK', df_['FloorPlanSTR'])

    # 7. FloorPlanSTR列が"DK"かつ、FloorPlanNumber列が1の行について、FloorPlanSTRを”K”にする
    df_['FloorPlanSTR'] = np.where((df_['FloorPlanSTR'] == 'DK') & (df_['FloorPlanNumber'] == '1'), 'K', df_['FloorPlanSTR'])

    # 8. FloorPlanSTR列が"LDK+S"の行について、FloorPlanNumberを+1して、FloorPlanSTRを"LDK"にする
    df_['FloorPlanNumber'] = np.where((df_['FloorPlanSTR'] == 'LDK+S'),
                                      df_['FloorPlanNumber'].astype(int) + 1, df_['FloorPlanNumber'])
    df_['FloorPlanSTR'] = np.where((df_['FloorPlanSTR'] == 'LDK+S'), 'LDK', df_['FloorPlanSTR'])

    # 9. FloorPlanSTR列が"DK+S"もしくは"DK+S"の行について、FloorPlanSTRを"LDK"にする
    df_['FloorPlanSTR'] = np.where((df_['FloorPlanSTR'] == 'DK+S') | (df_['FloorPlanSTR'] == 'K+S'), 'LDK', df_['FloorPlanSTR'])

    # 10. FloorPlan列を、FloorPlanNumber列とFloorPlanSTR列を連結した値で更新する
    df_['FloorPlan'] = df_['FloorPlanNumber'].astype(str) + df_['FloorPlanSTR']
    
    # 11. FloorPlanSTRがLDK、もしくはFloorPlanが1Kか1Rのもの以外は、FloorPlanを"others"に
    df_['FloorPlan'] = np.where(~((df_['FloorPlanSTR'] == 'LDK') | (df_['FloorPlan'].isin(['1K', '1R']))),
                            'others', df_['FloorPlan'])
    
    # 12. 元がNanのものはNanに戻す
    df_['FloorPlan'] = np.where(df_['FloorPlanOrigin'].isna(), np.nan, df_['FloorPlan'])
    
    # 13. 不要な列を削除
    df_ = df_.drop(['FloorPlanSTR', 'FloorPlanNumber'], axis=1)

    return df_


def make_save_file_name(areas_, from_and_to_, dir_path_):
        
    file_name_base = f"RealEstateData_{from_and_to_[0]}_{from_and_to_[1]}"
    for area in areas_:
        file_name_base += f"_{area}"
    
    file_name_main = dir_path_+file_name_base+"_main.csv"
    file_name_sub  = dir_path_+file_name_base+"_sub.csv"
    
    return file_name_main, file_name_sub