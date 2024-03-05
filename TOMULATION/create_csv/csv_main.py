#%%
"""
公開用コード
import datetime
import pandas as pd
from TOMULATION.create_csv.calc_diffusion_fraction  import *
from TOMULATION.create_csv.chamber import pick_up_chamber_data
from TOMULATION.create_csv.assimP import calculate_LPHCUR,LPHCUR
from TOMULATION.create_csv.weather_excel import temperature_outside_chamber
"""
"""
ローカル作業用コード
"""
import datetime
import pandas as pd
from create_csv.calc_diffusion_fraction  import *
from create_csv.chamber import pick_up_chamber_data
from create_csv.assimP import calculate_LPHCUR,LPHCUR
from create_csv.weather_excel import temperature_outside_chamber




def create_(g_prec_no,g_block_no,g_start_date,g_end_date,plantdata_excel_2hour,chamber_explanatory,nl1):
    plantdata_excel_2hour = plantdata_excel_2hour
    #気温等のチャンバデータ
    chamber_explanatory = chamber_explanatory
    #nl1ファイルを作成するためのベース
    nl1 = nl1

    df_chamber_explantory = pd.read_csv(chamber_explanatory)
    df_nl1 = pd.read_excel(nl1)
    df_nl1 = temperature_outside_chamber(chamber_explanatory,nl1)

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

    return df
