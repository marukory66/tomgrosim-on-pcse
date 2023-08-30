#%%
import matplotlib.pyplot as plt
import pandas as pd
import pcse
from pcse.models import Wofost72_WLP_FD
from pcse.fileinput import CABOFileReader,YAMLCropDataProvider,CSVWeatherDataProvider
from pcse.db import NASAPowerWeatherDataProvider
from pcse.util import WOFOST72SiteDataProvider
from pcse.base import ParameterProvider
from models import tomatomato
# -*- coding: utf-8 -*-
# Copyright (c) 2004-2017 Alterra, Wageningen-UR
# Allard de Wit (allard.dewit@wur.nl), February 2017
import glob
import os, sys
from urllib.request import urlopen
from urllib.error import URLError
import pickle
import yaml
from pcse.base import MultiCropDataProvider
from pcse import exceptions as exc
from pcse import settings
from pcse.util import version_tuple
import datetime
from create_csv.calc_diffusion_fraction import *
from create_csv.chamber import pick_up_chamber_data
from create_csv.assimP import calculate_LPHCUR,LPHCUR
from create_csv.weather_excel import temperature_outside_chamber
from create_csv.csv_main import create_
from input_data.main import _create_input_data

"""これらの数字をコマンドから持ってこれるようにする"""
g_prec_no = "51"
g_block_no = "47636"

"モデルを動かしたい期間中"
g_start_date = datetime.date(2019,12,25)
g_end_date = datetime.date(2020,6,5)

plantdata_excel_2hour = "C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse_pypl/PCSE/plantation_data/pi01_20191023_2hour.csv"
#気温等のチャンバデータ
chamber_explanatory = "C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse_pypl/PCSE/plantation_data/tomato_chamber_explanatory.csv"
#nl1ファイルを作成するためのベース
nl1 = "C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse/test_data/nl1.xls"

#1日ごとの気象データを与えるため
weatherfile = "C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse_pypl/PCSE/df.csv"
#各種パラメーターを取得，yamlの代わりここに実測光合成量用csvも格納
cropinitiallist = _create_input_data(glob.glob("C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse_pypl/PCSE/input_data/*.csv"))
#モデルの種類，Actual_measurement or Predict
modelkinds = "Predict"

campaign_start_date = "2019-12-25"
emergence_date = "2019-12-25"
harvest_date = "2020-01-24"
max_duration = "300"



"""ここまで"""

soil = CABOFileReader("C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse/test_data/ec3.soil")
cropd = YAMLCropDataProvider(fpath=r"C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse_pypl/PCSE/yaml")
cropd.set_active_crop('tomato','tomato_01')

#ここで，ファイルを作成するが気象庁からデータスクレイピングするために長時間必要のため
# に，前回までに作成している物を代用
df_assim_calculation = create_(g_prec_no,g_block_no,g_start_date,g_end_date,plantdata_excel_2hour,chamber_explanatory,nl1)


# df_assim_calculation_csv.to_csv('C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse_pypl/df_assim_calculation(EFF,PGMAX).csv')


# assim_calculation = "C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse_pypl/PCSE/df_assim_calculation(EFF,PGMAX).csv"
# df_assim_calculation = pd.read_csv(assim_calculation)

"""PCSEが使用できる形式にまとめる"""

site = WOFOST72SiteDataProvider(WAV=10,CO2=360)
parameterprovider = ParameterProvider(soildata=soil, cropdata=cropd, sitedata=site)

yaml_agro = """
- {start}:
    CropCalendar:
        crop_name: tomato
        variety_name: tomato
        crop_start_date: {startdate}
        crop_start_type: emergence
        crop_end_date: {enddate}
        crop_end_type: harvest
        max_duration: {maxdur}
    TimedEvents: null
    StateEvents: null
""".format(start=campaign_start_date, startdate=emergence_date,
           enddate=harvest_date, maxdur=max_duration)

weatherdataprovider = CSVWeatherDataProvider(weatherfile)
weathertimeseries = df_assim_calculation
agromanagement = yaml.load(yaml_agro,Loader=yaml.Loader)
wofost = tomatomato(parameterprovider,weatherdataprovider, agromanagement, weathertimeseries,cropinitiallist,modelkinds)

wofost.run_till_terminate()
output = wofost.my_get_output("C:/Users/maruko/Desktop/tomgro")
print("output",output)



# output = wofost.get_output()
# df = pd.DataFrame(output).set_index("day")
# df.tail()
