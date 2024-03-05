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
pattern = r'/d{4}[年/]/d{1,2}[月/]/d{1,2}日?'
from Greenhouse_environment_prediction_RF import Greenhouse_environment_prediction,Forming_nedo_data
from Photosynthesis_prediction_RF import Photosynthesis_prediction


#温室内環境予測RFモデル
# 外部環境から温室内の環境を予測するRFの目的変数(チャンバのcsv)
target_variables_csv = ""
# target_variables_csv = "20240101_2hour.csv"
#外部環境から温室内の環境を予測するRFの説明変数(気象庁一時間データ，チャンバの数値を取得した地域の値を使用)
object_variables_csv="宇和1時間気象データ.csv"
#作成した#温室内環境予測RFモデルの結果を出力するために使用するcsvの出力先
result_csv=""
#RFを作成する期間の開始日
model_startday = "2023/01/01 00:00:00"
#RFを作成する期間の終了日
model_endday = "2023/12/31 23:00:00"
#作成したRFを適応するcsvのパス　nedoのデータベース　地域はモデルを作成した地域と同地域
nedo_csv = "hm@@@@@year.csv"
#光合成予測したい4週間の開始日と終了日を与える
model_adaptation_variables,return_df = Forming_nedo_data(nedo_csv=nedo_csv,output_start_date="11月06",output_end_date="12月4")

#気象庁の環境データを説明変数にして，チャンバデータを目的変数としたRFに，NEDOの2週間データを与えて予測値を返す
df_Greenhouse_environment_prediction = (Greenhouse_environment_prediction(target_variables_csv=target_variables_csv,object_variables_csv=object_variables_csv,result_csv=result_csv,model_startday=model_startday,model_endday=model_endday,model_adaptation_variables=model_adaptation_variables,return_df=return_df))

#光合成予測RFモデル
#説明変数，目的変数共に同一のcsv内にあるため，pathは一つ
input_csv = ""
# input_csv = "20240101_2hour.csv"
#光合成予測RFモデルの結果をcsv出力するための引数
Photosynthesis_prediction_result_csv= ""
#光合成予測RFモデル予測開始日を定義します。モデル作成開始日は2週間前，モデル予測終了日は4週間後に自動で定義されます。
Model_predict_start_date = "2023/11/06 00:00:00"
Photosynthesis_model_adaptation_variables = df_Greenhouse_environment_prediction

result_Photosynthesis_prediction = Photosynthesis_prediction(input_csv=input_csv,Photosynthesis_prediction_result_csv=Photosynthesis_prediction_result_csv,Model_predict_start_date=Model_predict_start_date,Photosynthesis_model_adaptation_variables=Photosynthesis_model_adaptation_variables,return_df=return_df)
