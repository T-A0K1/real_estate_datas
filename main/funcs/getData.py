import requests
import pandas as pd

def getData(url, parameters):

    print(f'{parameters["area"]}のデータ取得を開始します')
    response = requests.get(url, params=parameters)
    print(f'{parameters["area"]}のデータ取得を完了しました')

    if response.status_code == 200:
        data = response.json()  # JSON形式のデータを取得
        df = pd.DataFrame(data['data'])
    else:
        print("Request was not successful. Status code:", response.status_code)
        
    return df
