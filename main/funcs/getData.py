import requests
import pandas as pd

def getData(url, parameters):

    response = requests.get(url, params=parameters)

    if response.status_code == 200:
        data = response.json()  # JSON形式のデータを取得
        df = pd.DataFrame(data['data'])
    else:
        print("Request was not successful. Status code:", response.status_code)
        
    return df
