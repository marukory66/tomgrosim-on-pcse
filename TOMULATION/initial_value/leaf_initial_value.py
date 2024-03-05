#%%
import pandas as pd
import csv
from datetime import datetime as dt
import math
from math import exp
import datetime

def Leaf_age(Leaf_area_csv):
    df_Leaf_age = pd.read_csv(Leaf_area_csv, encoding='SHIFT-JIS')
    ini_leaf_index = []
    for list_line_name,row in df_Leaf_age.iterrows():
        list_row = row.to_list()
        row_num = list_row[0]
        list_row = list_row[1:]
        for i,num in enumerate(list_row):
            if num != "None":
                ini_leaf_index.append((row_num-1)*7+1+i)
    total_leaf_index = []
    for i in range(1,300):
        total_leaf_index.append(i)
    for num in range(1,300):
        if (num > 8) and (num % 7 != 1) and (num % 7 != 2) and (num % 7 != 3):
            total_leaf_index.remove(num)
    Leaf_count = 0
    for tmp_leaf_index in reversed(total_leaf_index):
        if (tmp_leaf_index < ini_leaf_index[3]+28) and ( tmp_leaf_index >= ini_leaf_index[0]):
            Leaf_count +=1
            df_Leaf_age.iat[tmp_leaf_index//7,tmp_leaf_index%7] = Leaf_count*(7/3)
    return df_Leaf_age

def mesure_df_initial_Leaf_area(Leaf_area_csv,plant_density):
    ini_df_Leaf_area = pd.read_csv(Leaf_area_csv, encoding='SHIFT-JIS')
    for list_line_name,row in ini_df_Leaf_area.iterrows():
        list_row = row.to_list()
        row_num = list_row[0]
        list_row = list_row[1:]
        for i,num in enumerate(list_row):
            if num != "None":
                # tmp = float(num)*plant_density
                tmp = float(num)*plant_density
                ini_df_Leaf_area.iat[row_num-1,i+1] = tmp
    return ini_df_Leaf_area

#入力された値を基に，入力値間を補完
def initial_Leaf_area(Leaf_area_csv,plant_density):
    df_Leaf_area = pd.read_csv(Leaf_area_csv, encoding='SHIFT-JIS')
    #入力されている4つの葉の座標を入力
    ini_coordinate = []

    for list_line_name,row in df_Leaf_area.iterrows():
        list_row = row.to_list()
        row_num = list_row[0]
        list_row = list_row[1:]
        for i,num in enumerate(list_row):
            if num != "None":
                tmp_coordinate = row_num*7+i-7+1
                ini_coordinate.append(tmp_coordinate)
    total_number = []
    for i in range(1,300):
        total_number.append(i)
    #葉が存在することが出来ないセルを削除
    for num in range(1,300):
        if (num > 8) and (num % 7 != 1) and (num % 7 != 2) and (num % 7 != 3):
            total_number.remove(num)
    #スケルトンのtop50cm要面積で計測する2葉と一番下の葉の大きさを縦×横で入力。
    #(top50cmにおける)上位葉から中位葉までを入力
    up50leaf_minus_m50leaf = (ini_coordinate[-1]-ini_coordinate[-2])-(ini_coordinate[-1]-ini_coordinate[-2])//7*4
    m50leaf_index = total_number.index(ini_coordinate[-2])
    #ここで，葉ごとに数値を入力する。この際，ini_coordinate[3]とini_coordinate[2]の間を当分するコードを書き足す事も可能。
    m50leaf_value = df_Leaf_area.iloc[ini_coordinate[-2]//7,ini_coordinate[-2]%7]
    # mleaf_value = df_Leaf_area.iloc[11,2] 400
    for i in range(1,up50leaf_minus_m50leaf):
        tmp_index = total_number[m50leaf_index+i]
        df_Leaf_area.iat[tmp_index//7,tmp_index%7] = m50leaf_value

    #(top50cmにおける)中位葉から下位葉までを入力
    m50leaf_minus_un50leaf = (ini_coordinate[-2]-ini_coordinate[-3])-(ini_coordinate[-2]-ini_coordinate[-3])//7*4
    un50leaf_index = total_number.index(ini_coordinate[-3])
    un50leaf_value = df_Leaf_area.iloc[ini_coordinate[-3]//7,ini_coordinate[-3]%7]
    for i in range(1,m50leaf_minus_un50leaf):
        tmp_index = total_number[un50leaf_index+i]
        df_Leaf_area.iat[tmp_index//7,tmp_index%7] = un50leaf_value

    #上で入力した以外の，葉かきされていない葉を入力する。
    # Bottom_leafは葉かきされていない，一番下の葉
    un50leaf_minus_Bottom_leaf = (ini_coordinate[-3]-ini_coordinate[-4])-(ini_coordinate[-3]-ini_coordinate[-4])//7*4
    Bottom_leaf_index = total_number.index(ini_coordinate[-4])
    Bottom_leaf_value = df_Leaf_area.iloc[ini_coordinate[-4]//7,ini_coordinate[-4]%7]

    for i in range(1,un50leaf_minus_Bottom_leaf):
        tmp_index = total_number[Bottom_leaf_index+i]
        df_Leaf_area.iat[tmp_index//7,tmp_index%7] = Bottom_leaf_value
    ini_df_Leaf_area = df_Leaf_area

    #1219追記

    for list_line_name,row in ini_df_Leaf_area.iterrows():
        list_row = row.to_list()
        row_num = list_row[0]
        list_row = list_row[1:]
        for i,num in enumerate(list_row):
            if num != "None":
                tmp = float(num)*plant_density
                ini_df_Leaf_area.iat[row_num-1,i+1] = tmp

    return ini_df_Leaf_area


def Leaf_area(df_initial_Leaf_area,df_Leaf_age,today,temperature_csv,mesure_leaf_area,filling_rate,plant_density,POLA=0.104,POLB=0.136,POLC=13.6):

    df_temperature = pd.read_csv(temperature_csv, encoding='utf-8')
    df_Leaf_area = df_initial_Leaf_area
    for row in range(len(df_temperature["date"])):
        df_temperature.iat[row,0] = dt.strptime(df_temperature.iloc[row,0],"%Y/%m/%d")
        df_temperature.iat[row,0] = df_temperature.iat[row,0].date()
    tmp_top_leaf_age = 0
    for list_line_name,row in df_initial_Leaf_area.iterrows():
        list_row = row.to_list()
        row_num = list_row[0]
        list_row = list_row[1:]
        for i,num in enumerate(list_row):
            if num != "None":
                tmp_top_leaf_age = df_Leaf_age.iloc[row_num-1,i+1]
                # tmp_top_leaf_age = df_Leaf_age.iloc[row_num-1,i+1]*filling_rate*(1/10000)
        for i,num in enumerate(list_row):
            if num != "None":
                _tmp_Leaf_area = df_Leaf_area.iloc[row_num-1,i+1]
                df_Leaf_area.iat[row_num-1,i+1] = int(_tmp_Leaf_area)*filling_rate*(1/10000)

        for i,num in enumerate(list_row):
                if num == "None":
                    if df_Leaf_age.iloc[row_num-1,i+1] != "None":
                    # potential_leaf_area = POLA*exp(-POLB * (tmp_top_leaf_age - POLC))
                        potential_leaf_area = 0
                        potential_decimal = (math.modf(tmp_top_leaf_age)[0])
                        potential_decimal_point = str(potential_decimal)[2]
                        if potential_decimal_point != 0:
                            tmp_top_leaf_age = int(tmp_top_leaf_age)
                        elif potential_decimal_point == 3:
                            potential_leaf_area = (POLA*POLB*exp(-POLB * (math.ceil(tmp_top_leaf_age)- POLC)))*(1/3)
                            tmp_top_leaf_age = math.ceil(tmp_top_leaf_age)
                        elif potential_decimal_point == 6:
                            potential_leaf_area = (POLA*POLB*exp(-POLB * (math.ceil(tmp_top_leaf_age)- POLC)))*(2/3)
                            tmp_top_leaf_age = math.ceil(tmp_top_leaf_age)
                        for potential_temp_day in range(1,tmp_top_leaf_age):
                            potential_leaf_area =  potential_leaf_area + POLA*POLB*exp(-POLB * (potential_temp_day - POLC))

                        tmp_leaf_age = df_Leaf_age.iloc[row_num-1,i+1]
                        addition_tmp_Leaf_area = 0
                        decimal = (math.modf(tmp_leaf_age)[0])
                        decimal_point = str(decimal)[2]
                        if decimal_point != 0:
                            tmp_leaf_age = int(tmp_leaf_age)
                        elif decimal_point == 3:
                            addition_tmp_Leaf_area = (POLA*POLB*exp(-POLB * (math.ceil(tmp_leaf_age)- POLC)))*(1/3)
                            tmp_leaf_age = math.ceil(tmp_leaf_age)
                        elif decimal_point == 6:
                            addition_tmp_Leaf_area = (POLA*POLB*exp(-POLB * (math.ceil(tmp_leaf_age)- POLC)))*(2/3)
                            tmp_leaf_age = math.ceil(tmp_leaf_age)
                        for temp_day in range(1,tmp_leaf_age):
                            addition_tmp_Leaf_area =  addition_tmp_Leaf_area + POLA*POLB*exp(-POLB * (temp_day - POLC))
                            #実測した一番最小の葉の(実測値/ポテンシャル)をかけて補正する

                        _tmp_Leaf_area = (mesure_leaf_area/float(potential_leaf_area))*addition_tmp_Leaf_area*plant_density


                        df_Leaf_area.iat[row_num-1,i+1] = _tmp_Leaf_area
    return df_Leaf_area

def Leaf_harvest(Leaf_harvest_csv):
    df_Leaf_harvest_d = pd.read_csv(Leaf_harvest_csv, encoding='SHIFT-JIS')
    for list_line_name,row in df_Leaf_harvest_d.iterrows():
        list_row = row.to_list()
        row_num = list_row[0]
        list_row = list_row[1:]
        for i,num in enumerate(list_row):
            if num != "None":
                tmp = df_Leaf_harvest_d.iloc[row_num-1,i+1]
                if row_num == 1:
                    for k in range(1,i+1):
                        df_Leaf_harvest_d.iat[0,ii] = tmp
                if row_num != 1:
                    for k in range(1,8):
                        df_Leaf_harvest_d.iat[0,k] = tmp
                    for FL_row_num in range(1,row_num-1):
                        df_Leaf_harvest_d.iat[FL_row_num,1] = tmp
                        df_Leaf_harvest_d.iat[FL_row_num,2] = tmp
                        df_Leaf_harvest_d.iat[FL_row_num,3] = tmp
                    if i != 0:
                        for l in range(0,i):
                            df_Leaf_harvest_d.iat[row_num,l+1] = tmp
    return df_Leaf_harvest_d

def Leaf_weight(df_Leaf_area,weight_ratio):
    df_Leaf_weight = df_Leaf_area
    for list_line_name,row in df_Leaf_weight.iterrows():
        list_row = row.to_list()
        row_num = list_row[0]
        list_row = list_row[1:]
        for i,num in enumerate(list_row):
            if num != "None" :
                tmp = df_Leaf_weight.iloc[row_num-1,i+1]
                df_Leaf_weight.iat[row_num-1,i+1] = tmp*weight_ratio# 葉面積から葉の重量にする変換式をかます
    return df_Leaf_weight

def Leaf_dry_weight(df_Leaf_weight,dry_matter_percentage):
    df_Leaf_dry_weight = df_Leaf_weight
    for list_line_name,row in df_Leaf_dry_weight.iterrows():
        list_row = row.to_list()
        row_num = list_row[0]
        list_row = list_row[1:]
        for i,num in enumerate(list_row):
            if num != "None" :
                tmp = float(df_Leaf_dry_weight.iloc[row_num-1,i+1])
                df_Leaf_dry_weight.iat[row_num-1,i+1] = tmp*dry_matter_percentage
                # 葉の質量から乾物重に変換
    return df_Leaf_dry_weight

def specific_leaf_area(df_Leaf_area,DMC):
    df_specific_leaf_area = df_Leaf_area
    for list_line_name,row in df_specific_leaf_area.iterrows():
        list_row = row.to_list()
        row_num = list_row[0]
        list_row = list_row[1:]
        for i,num in enumerate(list_row):
            if num != "None" :
                tmp_Leaf_area = df_Leaf_area.iloc[row_num-1,i+1]
                tmp_DMC = DMC.iloc[row_num-1,i+1]
                if tmp_DMC != 0:
                    df_specific_leaf_area.iat[row_num-1,i+1] = tmp_Leaf_area/tmp_DMC
    return df_specific_leaf_area

def day_emergence_leaf(df_Leaf_age,day):
    s_format = '%Y-%m-%d'
    df_day_emergence_leaf = df_Leaf_age
    for list_line_name,row in df_day_emergence_leaf.iterrows():
        list_row = row.to_list()
        row_num = list_row[0]
        list_row = list_row[1:]
        for i,num in enumerate(list_row):
            if num != "None" :
                day = datetime.datetime.strptime(str(day), s_format)
                day = day.date()
                tmp_day_emergence_leaf = day + datetime.timedelta(days=-(float(num)))
                df_day_emergence_leaf.iat[row_num-1,i+1] = tmp_day_emergence_leaf
    return df_day_emergence_leaf
