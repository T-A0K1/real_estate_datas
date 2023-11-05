import pandas as pd

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
    after_len = df_.shape[1]
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
    