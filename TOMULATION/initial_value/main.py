#%%
import pandas as pd
import csv
import datetime
from leaf_initial_value import *
from fruit_initial_value import *
from datetime import datetime as dt
import math
from math import exp


#スケルトン計測日
#計測日を下記の形で代入
day = "2023-12-04"
# day = "2023-12-04"

#入力した最小の葉の縦×横m²
#入力した最小の葉の縦×横m²を入力
mesure_leaf_area = 0.005
#mesure_leaf_area = 0.005


# 全葉
#Leaf_area.csvのpathを指定
Leaf_area_csv = ""

#日付を気温を入力
#temperature.csvのpathを指定
temperature_csv = ""

#花房ごとに3つの果実の高さ(先，真ん中，根本)を入力
#Fruit_height_setting.csvのpathを指定
Fruit_height_setting = ""

#最後に葉かきした位置(第何花房の第何葉)にdayを記入
#Leaf_harvest_d.csvのpathを指定
Leaf_harvest_csv = ""

#leaf_age要leaf_area 一番上の葉，50cm内の中位葉，50cm内の下位葉，一番下の葉
#age_Leaf_area.csvのpathを指定
age_Leaf_area = ""


#葉の充填率
filling_rate = 0.2
#入力した最小の葉の葉面積
mesure_leaf_area = mesure_leaf_area*filling_rate
#果実の乾物率
fruit_dry_matter_percentage = 0.1
#葉の乾物率
Leaf_dry_matter_percentage = 0.08
#葉面積の生体重率 #葉縦×横(m2)から葉の重量gにする変換式
leaf_weight_ratio = 140
#果実の縦の長さ(mm)から生体重(g)に換算する式
#fruit_initial_valueのfruit_weight関数内に直接記入　
#栽植密度
plant_density=1
#ファイル保存用path
#作成した初期値を出力するpath
file_path = "TOMULATION/input_data/"


df_flowering_day = flowering_day(Leaf_area_csv=age_Leaf_area,day=day)
df_flowering_day.to_csv(file_path+"flowering_day.csv",index=None)
df_Leaf_age = Leaf_age(Leaf_area_csv=age_Leaf_area)
df_Leaf_age.to_csv(file_path+"LVAGE.csv",index=None)

#全実測値を使用
df_initial_Leaf_area = mesure_df_initial_Leaf_area(Leaf_area_csv=Leaf_area_csv,plant_density=plant_density)
df_initial_Leaf_area.to_csv(file_path+"df_initial_Leaf_area.csv",index=None)
df_Leaf_area = Leaf_area(df_initial_Leaf_area=df_initial_Leaf_area,df_Leaf_age=df_Leaf_age,today=day,temperature_csv=temperature_csv,mesure_leaf_area=mesure_leaf_area,filling_rate=filling_rate,plant_density=plant_density)
df_Leaf_area.to_csv(file_path+"LAI.csv",index=None)
df_fruit_weight = fruit_weight(Fruit_weight_setting=Fruit_height_setting,plant_density=plant_density)
df_fruit_weight.to_csv(file_path+"FFI.csv",index=None)
df_fruit_dry_weight = fruit_dry_weight(fruit_weight_df=df_fruit_weight,dry_matter_percentage=fruit_dry_matter_percentage)
df_fruit_dry_weight.to_csv(file_path+"FDI.csv",index=None)
df_fruit_dvs,df_day_emergence_fruit = fruit_dvs(df_flowering_day=df_flowering_day,df_fruit_weight=df_fruit_weight,today=day,temperature_csv=temperature_csv)
df_fruit_dvs.to_csv(file_path+"DVSFI.csv",index=None)
df_day_emergence_fruit.to_csv(file_path+"DOEFI.csv",index=None)
df_Leaf_weight = Leaf_weight(df_Leaf_area=df_Leaf_area,weight_ratio=leaf_weight_ratio)
df_Leaf_weight.to_csv(file_path+"LVI.csv",index=None)
df_Leaf_dry_weight = Leaf_dry_weight(df_Leaf_weight=df_Leaf_weight,dry_matter_percentage=Leaf_dry_matter_percentage)
df_Leaf_dry_weight.to_csv(file_path+"DMCI.csv",index=None)
df_day_emergence_leaf = day_emergence_leaf(df_Leaf_age,day)
df_day_emergence_leaf.to_csv(file_path+"DOELI.csv",index=None)
DOHLeaf = Leaf_harvest(Leaf_harvest_csv=Leaf_harvest_csv)
DOHLeaf.to_csv(file_path+"DOHLI.csv",index=None)