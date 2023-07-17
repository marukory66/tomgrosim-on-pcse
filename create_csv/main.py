#%%
import datetime
from calc_diffusion_fraction import *
import pandas as pd
from chamber import pick_up_chamber_data
from assimP import calculate_LPHCUR,LPHCUR
from weather_excel import temperature_outside_chamber

#これをコマンドで打たせたい
g_prec_no = "51"
g_block_no = "47636"
g_start_date = datetime.date(2019,12,25)
g_end_date = datetime.date(2020,6,5)
#plantdataの2時間応答のexcelファイル用引数
#日付データをそろえる必要あり
plantdata_excel_2hour = "C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse_pypl/plantation_data/pi01_20191023_2hour.csv"
#気温等のチャンバデータ
chamber_explanatory = "C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse_pypl/plantation_data/tomato_chamber_explanatory.csv"
#nl1ファイルを作成するためのベース
nl1 = "C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse/test_data/nl1.xls"



df_chamber_explantory = pd.read_csv(chamber_explanatory)
df_nl1 = pd.read_excel(nl1)
df_nl1 = temperature_outside_chamber(chamber_explanatory,nl1)

#weather
df_nl1.to_excel('C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse_pypl/df.xls',index = False)


#気象データ取得
ins = Diffusion()
df = ins.output(g_prec_no,g_block_no,g_start_date, g_end_date)
#2時間ごとの気象データ取得
df_2hour = get_2hour_ave(df)
#チャンバデータを取得して結合
df = pick_up_chamber_data(plantdata_excel_2hour,df_2hour)
#時間当たりの光合成量を取得
df = calculate_LPHCUR(df)
#計算結果のcsvを取得

df.to_csv('C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse_pypl/df_assim_calculation(EFF,PGMAX).csv')
