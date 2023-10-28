import requests
import pandas as pd

url = "https://www.land.mlit.go.jp/webland/api/TradeListSearch"
parameters = {
    "from": "20221",
    "to": "20224",
    "area": "01"
}

response = requests.get(url, params=parameters)

if response.status_code == 200:
    data = response.json()  # JSON形式のデータを取得
    # 取得したデータを使って何かしらの処理を行う
    df = pd.DataFrame(data)
    print(data.head())  # ここでは単純にデータを表示している例
else:
    print("Request was not successful. Status code:", response.status_code)
