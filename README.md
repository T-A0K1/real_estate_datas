# real_estate_datas

# 概要
不動産取引価格情報取得API（国交省）のデータを取得して、いじる
- https://www.land.mlit.go.jp/webland/api.html

# データ仕様(データ例は、北海道の20221-20224で確認、Typeが農地、林地は除外)
## 不要な列
- PricePerUnit
- UnitPrice
- Purpose
- Direction
- Classification
- Remarks:nanだけに絞りたい

## 各列の概要
- Type: 取引の種類['宅地(土地と建物)', '中古マンション等', '宅地(土地)', '農地', '林地']
- Region:['住宅地', nan, '商業地', '工業地', '宅地見込地']
- MunicipalityCode: 市区町村コード(5桁の数字)
- Prefecture: 都道府県(文字列) ex:北海道
- Municipality: 市区町村名(文字列) ex:札幌市中央区
- DistrictName: 地区名 ex:旭ヶ丘 大通り西
- TradePrice: 価格(astype('int')可能)
- PricePerUnit: 坪単価(astype('float')可能　Nanあり)
- Area: 面積 「㎡以上」の文字列を除去すればint可能(['2000㎡以上', '5000㎡以上']の二つがあるっぽい)
- LandShape: ['台形', nan, '長方形', 'ほぼ整形', '不整形', 'ほぼ長方形', 'ほぼ正方形', '正方形', 'ほぼ台形','袋地等']
- Frontage: 間口。道路や通りに面する長さ。2m未満は再建築不可のため、よろしくない。m2抜きで、floatOK
- UnitPrice: 取引価格(平方メートル単価):float
- TotalFloorArea: 延床面積。建物面積ともいう。「㎡以上」文字列除去でfloat可能
- BuildingYear: 築年。(なんで和暦なんだよ)['平成2年', '平成19年',戦前、nan...]
- Structure: ['木造', 'ＲＣ', 'ＳＲＣ', nan, '鉄骨造', '軽量鉄骨造', 'ＲＣ、木造', 'ブロック造', 'ＲＣ、鉄骨造','鉄骨造、木造', '木造、ブロック造', 'ＲＣ、ブロック造']
- Use: 用途。['住宅', nan, '共同住宅',..]。住宅と共同住宅が大半
- Purpose:今後の利用目的。古いデータにはないので注意。['住宅', 'その他', '店舗', '事務所', nan, '工場', '倉庫']
- Direction: 前面道路の方位
- Classification: 前面道路の種類(私道、国道、県道 etc)
- Breadth: 全面道路の道幅。floatOK
- CityPlanning: 都市計画。['第１種住居地域', '商業地域'..]。参考：https://iqrafudosan.com/channel/urban-planning-japan
- CoverageRatio: 建蔽率。だいたい60%が多い。用途地域によって制限があるぽい。nanあるが、n*10の数字
- FloorAreaRatio: 容積率。用途地域によって制限がある
- Period: 取引時期 パラメータで指定するやつ。['2022年第１四半期', '2022年第４四半期'...]
- FloorPlan: [nan, '２ＬＤＫ', '３ＬＤＫ', '１Ｒ＋Ｓ'...]
- Renovation: 改装有無。[nan, '改装済', '未改装']
- Remarks:取引の事情等。[nan, '調停・競売等', '私道を含む取引', '隣地の購入', '関係者間取引', '古屋付き・取壊し前提']。大半がNan

## 各列の下処理
正規化をするかどうか。
- Type: 特になし
- Region: 特になし
- MunicipalityCode: 特になし
- Prefecture: コード化して正規化するかどうか
- DistrictName: 特になし
- TradePrice: int、万円にする
- PricePerUnit: float
- Area: m2消す、float
- LandShape; 特になし
- Frontage: m2消す、float
- UnitPrice: float
- TotalFloorArea: m2消す、float
- BuildingYear: 西暦に直す+築年列を作る
- Structure: 特になし
- Use: 特になし
- Purpose: 特になし
- Direction: 特になし
- Classification: 特になし
- Breadth: 特になし
- CityPlanning: 特になし。ちょっと正規化したい
- CoverageRatio: float
- FloorAreaRatio: float
- Period: XXXX年第Y四半期を年とYに分ける
- FloorPlan: 特になし
- Renovation: 特になし
- Remarks: 特になし。

## 行の削除
最低限にする
Type: ['宅地(土地と建物)', '中古マンション等', '宅地(土地)']に絞る
Remarks: nanに絞る