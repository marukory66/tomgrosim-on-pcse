#%%
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split#データ分割用
from sklearn.ensemble import RandomForestRegressor#ランダムフォレスト
import lightgbm as lgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error
from sklearn.metrics import r2_score
from sklearn.tree import export_graphviz
import pickle
import re
import datetime
pattern = r'\d{4}[年/]\d{1,2}[月/]\d{1,2}日?'

def Photosynthesis_prediction(input_csv,Photosynthesis_prediction_result_csv,Model_predict_start_date,Photosynthesis_model_adaptation_variables,return_df):

    """_summary_
    RFは過去2週間の内部環境データから2週間先の光合成量を予測します。
    Args:
        input_csv (_type_):説明変数として,チャンバの気温・日射・胞差・co2濃度を使用する
        目的変数として，チャンバの光合成量を使用する
        このため,一つのcsvでモデルを作成する
        Photosynthesis_prediction_result_csv (_type_): RFの結果を出力するcsvのpath
        Model_predict_start_date (_type_): モデル予測開始日を定義する,モデル作成開始日は2週間前,モデル予測終了日は2週間後
    """

    base_df = pd.read_csv(input_csv)
    base_df = base_df.drop(list(base_df[base_df["enable"] != True].index))
    base_df = base_df.reset_index()


    datetime_base_date = datetime.datetime.strptime(Model_predict_start_date, '%Y/%m/%d %H:%M:%S')
    model_start_date = datetime_base_date - datetime.timedelta(days=14)
    model_start_date = Model_predict_start_date + " JST"
    model_end_date = datetime_base_date + datetime.timedelta(days=14)
    model_end_date = model_end_date.strftime("%Y/%m/%d %H:%M:%S") +  " JST"
    predict_start_date = datetime_base_date
    predict_end_date = datetime_base_date + datetime.timedelta(days=28)
    predict_end_date = predict_end_date.strftime("%Y/%m/%d %H:%M:%S") +  " JST"
    csv_predict_end_date = datetime_base_date + datetime.timedelta(days=27)
    csv_predict_end_date = csv_predict_end_date.strftime("%Y/%m/%d %H:%M:%S") +  " JST"
    base_df = base_df[base_df["Date"] >= model_start_date]
    base_df = base_df[base_df["Date"] <  model_end_date]
    # 学習データとテストデータに分割します。
    #目的変数
    y = base_df["Photosynthetic.rate"]
    #説明変数
    x = base_df[["Vapor.pressure.deficit","Temperature.outside.chamber","Solar.radiation","CO2.concentration.air.sampling.average"]]

    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3,random_state=0)
    # モデルの形式を指定します。
    # max_depth＝レイヤの数、n_estimators = 木の本数,random_state　= 乱数の設定
    clf = RandomForestRegressor(max_depth=5,n_estimators=100,random_state=0)
    # モデル作成を実行します。（説明変数、目的変数）
    clf.fit(x_train, y_train)
    Photosynthesis_model_adaptation_variables=Photosynthesis_model_adaptation_variables[["Vapor.pressure.deficit","Temperature.outside.chamber","Solar.radiation","CO2.concentration.air.sampling.average"]]
    predict_Photosynthesis = clf.predict(Photosynthesis_model_adaptation_variables)
    dfobj = pd.DataFrame(columns=[])
    return_df = return_df[::2]
    dfobj["Date"] = return_df["Date"].to_list()
    dfobj["predict_Photosynthesis"] = predict_Photosynthesis
    dfobj = dfobj.assign(R2="")
    dfobj.to_csv(Photosynthesis_prediction_result_csv)
    return dfobj
