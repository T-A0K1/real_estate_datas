import pandas as pd

def RemoveM2(df_, needRemoveVal:dict):
    # target_wordの文字を含むデータのtarget_wordを除去
    # 新規列を追加し、除去した行はフラグを立てる
    for col, target_word in needRemoveVal.items():
        new_col = col+'_over_flag'
        target_row = df_.loc[:, col].str.contains(target_word).fillna(False)
        print(col, target_word, sum(target_row))
        df_[new_col] = 0
        df_.loc[target_row, new_col] = 1
        df_[col] = df_.loc[:,col].str.replace(target_word,'')
        
    return df_

def changeDataType(df_,changeDataTypeVal:dict):
    for col,new_data_type in changeDataTypeVal.items():
        print(col,new_data_type)
        df_[col] = df_.loc[:,col].astype(new_data_type)
    return df_