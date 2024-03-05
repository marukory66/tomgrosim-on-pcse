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
import datetime
from datetime import datetime as dt
import re
import copy

def Forming_nedo_data(nedo_csv,output_start_date,output_end_date):
    """nedoの値を整理するための関数

    Args:
        nedo_csv (_type_): nedoのCSVのpathを想定
        output_start_date (_type_): 抽出する期間の開始日 "01/01" この形を想定，使いやすい形にするのは後で
        output_end_date (_type_): 抽出する期間の終了日
    """
    col_name = range(1,34,1)
    df_nedo_csv = pd.read_csv(nedo_csv,names=col_name)
    df_nedo_csv = df_nedo_csv.fillna("")
    df_nedo_csv = df_nedo_csv.drop(df_nedo_csv.index[0])
    df_nedo_csv = df_nedo_csv[df_nedo_csv[1].isin([1,5,8])]
    df_nedo_csv = df_nedo_csv.reset_index()
    row_date = []


    for i in range(len(df_nedo_csv[4])):
        row_date.append(datetime.datetime(int(df_nedo_csv[4][i]),int(df_nedo_csv[2][i]),int(df_nedo_csv[3][i])))
    df_nedo_csv["Date"] = row_date

    df_nedo_csv = df_nedo_csv[["Date",1,5,6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25,26,27,28]]

    df_nedo_csv.columns = ["Date","environmental_element_number","01:00:00 JST","02:00:00 JST","03:00:00 JST","04:00:00 JST","05:00:00 JST","06:00:00 JST","07:00:00 JST","08:00:00 JST","09:00:00 JST","10:00:00 JST","11:00:00 JST","12:00:00 JST","13:00:00 JST","14:00:00 JST","15:00:00 JST","16:00:00 JST","17:00:00 JST","18:00:00 JST","19:00:00 JST","20:00:00 JST","21:00:00 JST","22:00:00 JST","23:00:00 JST","24:00:00 JST"]

    cols = ["Date","solar_radiation","temperature","Precipitation"]

    df_1 = pd.DataFrame(index=[], columns=cols)
    for i in range(0,len(df_nedo_csv["Date"]),3):
        tmp_df_nedo_csv = df_nedo_csv[i:i+3]
        Day = tmp_df_nedo_csv["Date"].iloc[1].strftime("%Y年%m月%d")
        tmp_df_nedo_csv = tmp_df_nedo_csv.drop("Date",axis=1)
        tmp_df_nedo_csv = tmp_df_nedo_csv.T
        tmp_df_nedo_csv = tmp_df_nedo_csv[1:25]
        tmp_df_nedo_csv.index = [Day + " 01:00:00 JST",Day +" 02:00:00 JST",Day +" 03:00:00 JST",Day+" 04:00:00 JST",Day +" 05:00:00 JST",Day +" 06:00:00 JST",Day + " 07:00:00 JST",Day +" 08:00:00 JST",Day +" 09:00:00 JST",Day + " 10:00:00 JST",Day +" 11:00:00 JST",Day +" 12:00:00 JST",Day +" 13:00:00 JST",Day + " 14:00:00 JST",Day +" 15:00:00 JST",Day +" 16:00:00 JST",Day +" 17:00:00 JST",Day + " 18:00:00 JST",Day +" 19:00:00 JST",Day +" 20:00:00 JST",Day +" 21:00:00 JST",Day + " 22:00:00 JST",Day +" 23:00:00 JST",Day +" 24:00:00 JST"]
        tmp_df_nedo_csv = tmp_df_nedo_csv.reset_index()
        tmp_df_nedo_csv.columns = ["Date","solar_radiation","temperature","Precipitation"]
        tmp_df_nedo_csv = tmp_df_nedo_csv.rename(columns={'index': 'Date'})
        df_1 = pd.concat([df_1,tmp_df_nedo_csv],axis=0)
    df_1 = df_1.reset_index()
    start_date = (df_1["Date"].str.contains(output_start_date))
    start_date = start_date[start_date==True]
    csv_start_date = (start_date.index[0])
    end_date = (df_1["Date"].str.contains(output_end_date))
    end_date = end_date[end_date==True]
    csv_end_date = (end_date.index[0])+24


    df = pd.DataFrame(index=[], columns=cols)
    for i in range(0,len(df_nedo_csv["Date"]),3):
        tmp_df_nedo_csv = df_nedo_csv[i:i+3]
        Day = tmp_df_nedo_csv["Date"].iloc[1].strftime("%Y/%m/%d")
        tmp_df_nedo_csv = tmp_df_nedo_csv.drop("Date",axis=1)
        tmp_df_nedo_csv = tmp_df_nedo_csv.T
        tmp_df_nedo_csv = tmp_df_nedo_csv[1:25]
        tmp_df_nedo_csv.index = [Day + " 01:00:00 JST",Day +" 02:00:00 JST",Day +" 03:00:00 JST",Day+" 04:00:00 JST",Day +" 05:00:00 JST",Day +" 06:00:00 JST",Day + " 07:00:00 JST",Day +" 08:00:00 JST",Day +" 09:00:00 JST",Day + " 10:00:00 JST",Day +" 11:00:00 JST",Day +" 12:00:00 JST",Day +" 13:00:00 JST",Day + " 14:00:00 JST",Day +" 15:00:00 JST",Day +" 16:00:00 JST",Day +" 17:00:00 JST",Day + " 18:00:00 JST",Day +" 19:00:00 JST",Day +" 20:00:00 JST",Day +" 21:00:00 JST",Day + " 22:00:00 JST",Day +" 23:00:00 JST",Day +" 24:00:00 JST"]
        tmp_df_nedo_csv = tmp_df_nedo_csv.reset_index()
        tmp_df_nedo_csv.columns = ["Date","solar_radiation","temperature","Precipitation"]
        tmp_df_nedo_csv = tmp_df_nedo_csv.rename(columns={'index': 'Date'})
        df = pd.concat([df,tmp_df_nedo_csv],axis=0)

    df = df.reset_index()
    #気象庁のデータに合わせる
    df["solar_radiation"] = df["solar_radiation"]/float(100)
    df["temperature"] = df["temperature"]/float(10)
    df["Precipitation"] = df["Precipitation"]/float(10)


    df = df[csv_start_date:csv_end_date]
    return_df = copy.deepcopy(df)
    df = df.reset_index()
    T_2h = []
    C_2h = []
    solar = []
    Date = []
    for i in range(0,len(df["temperature"]),2):
        Date.append(df["Date"][i])
        t1 = float(df["temperature"][i])
        t2 = float(df["temperature"][i+1])
        T_2h.append(round((t1+t2)/2,1))
        c1 = float(df["Precipitation"][i])
        c2 = float(df["Precipitation"][i+1])
        C_2h.append(round((c1+c2)/2,1))
        v1 = float(df["solar_radiation"][i])
        v2 = float(df["solar_radiation"][i+1])
        solar.append(round((v1+v2)/2,1))
    df_object_variables = pd.DataFrame(index=[], columns=[])
    df_object_variables["Date"] = Date
    df_object_variables["t_2h"] = T_2h
    df_object_variables["c_2h"] = C_2h
    df_object_variables["solar"] = solar
    return df_object_variables,return_df


def Greenhouse_environment_prediction(target_variables_csv,object_variables_csv,result_csv,model_startday,model_endday,model_adaptation_variables,return_df):

    """_summary_
    Args:
        target_variables_csv (_type_): 目的変数となる列が記載されているcsv,気温・日射・胞差・co2濃度
        object_variables_csv (_type_): 説明変数となる列が記載されているcsv,気象庁の環境データcsvを想定,気温・日射・降水量
        result_csv (_type_): RF自体の評価の為のCSV出力用path
        model_startday (_type_): 作成したいRFの初期日を指定
        model_endday (_type_): 作成したいRFの最終日日を指定
        model_adaptation_variables: 作成したRFを適応させるcsv
    Returns:
        _type_: 指定した期間の気温・日射・ほうさ・CO2濃度の予測値を返す
    """

    df_target_variables = pd.read_csv(target_variables_csv)
    temp_base_df = df_target_variables
    false_list = list(df_target_variables
    [df_target_variables["enable"] != True].index)

    false_date_list = []
    for i in range(len(false_list)):
        index = false_list[i]
        false_date_list.append(df_target_variables["Date"][index])
    #モデル作成日時と合わせています
    df_target_variables = df_target_variables[df_target_variables["Date"] > model_startday +" JST"]
    df_target_variables = df_target_variables[df_target_variables["Date"] <= model_endday +" JST"]
    df_object_variables = pd.read_csv(object_variables_csv,encoding="cp932")
    df_target_variables = df_target_variables.reset_index(drop=True)
    t_2h = []
    c_2h = []
    solar = []
    for i in range(0,len(df_object_variables["気温(℃)"]),2):
        t1 = float(df_object_variables["気温(℃)"][i])
        t2 = float(df_object_variables["気温(℃)"][i+1])
        t_2h.append(round((t1+t2)/2,1))
        c1 = float(df_object_variables["降水量(mm)"][i])
        c2 = float(df_object_variables["降水量(mm)"][i+1])
        c_2h.append(round((c1+c2)/2,1))
        v1 = float(df_object_variables["日射量(MJ/㎡)"][i])
        v2 = float(df_object_variables["日射量(MJ/㎡)"][i+1])
        solar.append(round((v1+v2)/2,1))
    df_target_variables["t_2h"] = t_2h
    df_target_variables["c_2h"] = c_2h
    df_target_variables["solar"] = solar
    #目的変数
    y = df_target_variables[["Vapor.pressure.deficit","Temperature.outside.chamber","Solar.radiation","CO2.concentration.air.sampling.average"]]
    #説明変数
    x = df_target_variables[["t_2h","c_2h","solar"]]
    # 学習データとテストデータに分割します。
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=0.3,random_state=0)
    # モデルの形式を指定します。
    # max_depth＝レイヤの数、n_estimators = 木の本数,random_state　= 乱数の設定
    clf = RandomForestRegressor(max_depth=5,n_estimators=100,random_state=0)
    # モデル作成を実行します。（説明変数、目的変数）
    clf.fit(x_train, y_train)
    # モデル作成に用いた（このデータを使って作られている）Trainデータを用いて予測します。
    y_predict_train = clf.predict(x_train)
    # CSVで結果を出力するために１列目がy_predict_train，２列めがy_trainのデータを作成します。
    np_list_1=[y_predict_train, y_train]
    # モデル作成に用いていない（モデルにとっては初見となる）データを用いて予測します。
    # y_predict_test  = clf.predict(model_adaptation_variables[['t_2h', 'c_2h', 'solar']])

    df_target_variables = df_target_variables.reset_index()
    #モデルの出力結果をまとめるDFを作成

    name_list = ["Vapor.pressure.deficit","Temperature.outside.chamber","Solar.radiation","CO2.concentration.air.sampling.average"]
    pre_name_list = ["predict_Vapor.pressure.deficit","predict_Temperature.outside.chamber","predict_Solar.radiation","predict_CO2.concentration.air.sampling.average"]

    y_predict_test  = clf.predict(model_adaptation_variables[['t_2h', 'c_2h', 'solar']])
    return_df = return_df.reset_index()
    return_df = return_df[::2]
    #目的変数をまとめる
    #base_dateを元に過去2週間の説明変数を元に未来の2週間分の環境を予測します
    return_dfobj =  pd.DataFrame(columns=[])
    for i in range(y_predict_train.shape[1]):
        return_dfobj[name_list[i]] = y_predict_test[:,i]
    return_dfobj["Date"] = return_df["Date"].to_list()

    return return_dfobj
