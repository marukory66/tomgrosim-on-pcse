#%%
import pandas as pd
import csv
from datetime import datetime as dt
import math
from math import exp
import datetime
import copy

def flowering_day(Leaf_area_csv,day):
    df_flowering_day = pd.read_csv(Leaf_area_csv, encoding='SHIFT-JIS')
    up50flowe_truss_num = 0
    for list_line_name,row in df_flowering_day.iterrows():
        list_row = row.to_list()
        row_num = list_row[0]
        list_row = list_row[1:]
        for i,num in enumerate(list_row):
            if num != "None":
                df_flowering_day.iat[row_num-1,i+1] = "None"
                up50flowe_truss_num = row_num
    s_format = '%Y-%m-%d'
    day = datetime.datetime.strptime(day, s_format)
    day = day.date()
    F_flowering_day=7
    for i,tmp_truss in enumerate(reversed(range(up50flowe_truss_num))):
        tmp_day = 7*i
        F_flowering_day += 7
        df_flowering_day.iat[tmp_truss+1,1] = day-datetime.timedelta(tmp_day)
    # df_flowering_day.iat[0,1] = day-datetime.timedelta(F_flowering_day)
    df_flowering_day.iat[0,1] = day-datetime.timedelta(F_flowering_day-7)
    return df_flowering_day

def calculation_fruit_emergence_day(fruits_of_truss,n,df_fruit_dvs,row_num,lowering_date_of_truss):
    tmp_numbers = list(range(0,fruits_of_truss))
    tmp_fruits_of_truss = [tmp_numbers[idx:idx + n] for idx in range(0,len(tmp_numbers), n)]

    if n == 3:
        if fruits_of_truss % 3 == 0:
            for i,fruit_location_num in enumerate(range(((fruits_of_truss)//n))):
                for k in tmp_fruits_of_truss[fruit_location_num]:
                    df_fruit_dvs.iat[row_num-1,k+1] = lowering_date_of_truss + datetime.timedelta(i)
        else:
            for i,fruit_location_num in enumerate(range(((fruits_of_truss//n)+1))):
                for k in tmp_fruits_of_truss[fruit_location_num]:
                    df_fruit_dvs.iat[row_num-1,k+1] = lowering_date_of_truss + datetime.timedelta(i)

    if fruits_of_truss % 2 == 0:
        for i,fruit_location_num in enumerate(range(((fruits_of_truss)//n))):
            for k in tmp_fruits_of_truss[fruit_location_num]:
                df_fruit_dvs.iat[row_num-1,k+1] = lowering_date_of_truss + datetime.timedelta(i)
    else:
        for i,fruit_location_num in enumerate(range(((fruits_of_truss)//n)+1)):
            for k in tmp_fruits_of_truss[fruit_location_num]:
                df_fruit_dvs.iat[row_num-1,k+1] = lowering_date_of_truss + datetime.timedelta(i)

#dvsの計算部分 phenology参照
def _dev_rate_fruit(drvTEMP,sDVSF):
    rDVRF = 0.0181 + math.log(drvTEMP/20) * (0.0392 - 0.213 * sDVSF + 0.415 * sDVSF**2 - 0.24 * sDVSF**3)
    return(rDVRF)

def fruit_dvs(df_flowering_day,df_fruit_weight,today,temperature_csv):
    s_format = '%Y-%m-%d'
    today = datetime.datetime.strptime(today, s_format)
    today = today.date()
    df_fruit_dvs = df_fruit_weight

    for list_line_name,row in df_fruit_dvs.iterrows():
        list_row = row.to_list()
        row_num = list_row[0]
        list_row = list_row[1:]
        fruits_of_truss = 0
        for num in list_row:
            if num != "None":
                fruits_of_truss += 1
        if fruits_of_truss >3:
            lowering_date_of_truss = df_flowering_day.iloc[row_num-1,1]
        tmp_numbers = list(range(0,fruits_of_truss))

        #果実数により，何房かに分かれていると定義して日付を付与する 房数は変数nで定義
        if (3 <= fruits_of_truss) and (fruits_of_truss <= 10):
            for i,fruit_location_num in enumerate(range(1,fruits_of_truss+1)):
                df_fruit_dvs.iat[row_num-1,fruit_location_num] = lowering_date_of_truss + datetime.timedelta(i)
        if 10 < fruits_of_truss:
            if 10 < fruits_of_truss <= 20:
                calculation_fruit_emergence_day(fruits_of_truss=fruits_of_truss,n=2,df_fruit_dvs=df_fruit_dvs,row_num=row_num,
        lowering_date_of_truss=lowering_date_of_truss)
            elif 20 < fruits_of_truss <= 30:
                calculation_fruit_emergence_day(fruits_of_truss=fruits_of_truss,n=3,df_fruit_dvs=df_fruit_dvs,row_num=row_num,
        lowering_date_of_truss=lowering_date_of_truss)
            elif 30 < fruits_of_truss <= 40:
                calculation_fruit_emergence_day(fruits_of_truss=fruits_of_truss,n=4,df_fruit_dvs=df_fruit_dvs,row_num=row_num,
        lowering_date_of_truss=lowering_date_of_truss)
            elif 40 < fruits_of_truss <= 50:
                calculation_fruit_emergence_day(fruits_of_truss=fruits_of_truss,n=5,df_fruit_dvs=df_fruit_dvs,row_num=row_num,
        lowering_date_of_truss=lowering_date_of_truss)
            elif 50 < fruits_of_truss <= 60:
                calculation_fruit_emergence_day(fruits_of_truss=fruits_of_truss,n=6,df_fruit_dvs=df_fruit_dvs,row_num=row_num,
        lowering_date_of_truss=lowering_date_of_truss)

        # lowering_date_of_truss=lowering_date_of_truss)

    #果実の出現日df
    df_day_emergence_fruit = copy.deepcopy(df_fruit_dvs)

    #ここまでで，各果実が出現してからの日数を定義したので，これにdef rate fruitを与えて計算させる
    df_temperature = pd.read_csv(temperature_csv, encoding='utf-8')
    for row in range(len(df_temperature["date"])):
        df_temperature.iat[row,0] = dt.strptime(df_temperature.iloc[row,0],"%Y/%m/%d")
        df_temperature.iat[row,0] = df_temperature.iat[row,0].date()
    today_temperature = df_temperature[df_temperature["date"] == today]
    today_temperature_num = today_temperature.index[0]
    for list_line_name,row in df_fruit_dvs.iterrows():
        list_row = row.to_list()
        row_num = list_row[0]
        list_row = list_row[1:]
        for index,num in enumerate(list_row):
            if num != "None":
                tmp_date = df_fruit_dvs.iloc[row_num-1,index+1]
                tmp_temperature = df_temperature[df_temperature["date"] == tmp_date]
                tmp_temperature_num = tmp_temperature.index[0]
                sDVSF = 0
                for i,Number_of_days in enumerate(range(tmp_temperature_num,today_temperature_num)):
                    sdvs = _dev_rate_fruit(df_temperature.iloc[Number_of_days,1],sDVSF)
                    sDVSF = sDVSF + sdvs
                df_fruit_dvs.iat[row_num-1,index+1] = sDVSF
    return df_fruit_dvs,df_day_emergence_fruit

def fruit_weight(Fruit_weight_setting,plant_density):
    """_summary_

    Args:
        path : 果実の高さを計測した値を入れたcsvのpath
        各花房に3つの個体を計測することを想定(根元,真ん中,先端の3個体)
    """

    fruit_weight_df = pd.read_csv(Fruit_weight_setting,
    encoding='SHIFT-JIS')
    ini_w = {}
    for list_line_name,row in fruit_weight_df.iterrows():
        list_row = row.to_list()
        row_num = list_row[0]
        list_row = list_row[1:]
        for i,num in enumerate(list_row):
            if num != "None":
                tmp = fruit_weight_df.iloc[row_num-1,i+1]
                tmp = float(tmp)
                fruit_weight_df.iat[row_num-1,i+1] = tmp
    for list_line_name,row in fruit_weight_df.iterrows():
        list_row = row.to_list()
        row_num = list_row[0]
        list_row = list_row[1:]
        tmp_list = []
        for i in range(len(list_row)):
            if type(list_row[i]) != str:
                tmp_list.append(list_row[i])
        if len(tmp_list) != 0:
            ini_w[row_num] = tmp_list
            f_w = list_row.index(tmp_list[0])
            s_w = list_row.index(tmp_list[1])
            t_w = list_row.index(tmp_list[2])
            First_half_tmp_value = list_row[f_w] - list_row[s_w]
            First_half_tmp_value = First_half_tmp_value/(s_w)
            for i in range(2,(s_w)+1):
                fruit_weight_df.iat[row_num-1,i] = (list_row[f_w] - (i-1)*First_half_tmp_value)
            Latter_half_tmp_value = list_row[s_w] - list_row[t_w]
            Latter_half_tmp_value = Latter_half_tmp_value/(t_w-s_w)
            for i in range((s_w)+1,(t_w)):
                fruit_weight_df.iat[row_num-1,i+1] = (list_row[s_w] - (i-(s_w))*Latter_half_tmp_value)
    for list_line_name,row in fruit_weight_df.iterrows():
        list_row = row.to_list()
        row_num = list_row[0]
        list_row = list_row[1:]
        for i,num in enumerate(list_row):
            if num != "None":
                tmp_fruit_weight = fruit_weight_df.iloc[row_num-1,i+1]
                # tmp_fruit_weight = tmp_fruit_weight*Conversion_formula*plant_density

                tmp_fruit_weight = ((0.0005*tmp_fruit_weight**3)-(0.0144*tmp_fruit_weight**2)+(0.2014*tmp_fruit_weight))*plant_density

                fruit_weight_df.iat[row_num-1,i+1] = tmp_fruit_weight
    return fruit_weight_df

def fruit_dry_weight(fruit_weight_df,dry_matter_percentage):
    """_summary_
    Args:
        fruit_weight_df 果実の生体重
        果実の生体重が設定されているセルに対して，乾物率をかけて果実の乾物重としている
    """
    fruit_dry_weight_df = fruit_weight_df
    for list_line_name,row in fruit_weight_df.iterrows():
        list_row = row.to_list()
        row_num = list_row[0]
        list_row = list_row[1:]
        for i,num in enumerate(list_row):
            if num != "None":
                tmp = fruit_weight_df.iloc[row_num-1,i+1]
                tmp = tmp*dry_matter_percentage
                fruit_dry_weight_df.iat[row_num-1,i+1] = tmp
    return fruit_dry_weight_df
