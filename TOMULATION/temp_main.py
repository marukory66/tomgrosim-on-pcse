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

class TOMULATION():
    def __init__():
        pass
    def main():
        pass


#予測モデルを使用する際の気象データを取得する
g_prec_no = "73"
g_block_no = "47887"
g_start_date = datetime.date(2023,10,23)
g_end_date = datetime.date(2023,11,20)


#モデルを動かしたい日から最終日までの2時間ごとのチャンバ計測csv 例)20240101_2hour
plantdata_excel_2hour = ""

#チャンバの日ごとの気象データcsv 例)tomato_chamber_explanatory例)tomato_chamber_explanatory
chamber_explanatory = ""
#nl1ファイルを作成するためのベースpath nl1.xls　変更不要
nl1 = "nl1.xls"

#df.csvのpath df.csv
weatherfile = "df.csv"

#glob.glob(C:/Users/・・・/inpt_data/*.csvで指定して各種初期値を取得する
cropinitiallist = _create_input_data(glob.glob("/input_data/*.csv"))
#モデルの種類を選択　Actual_measurement or Predict
modelkinds = "Actual_measurement"

campaign_start_date = "2023-12-04"
emergence_date = "2023-12-04"
# emergence_date モデル開始日
harvest_date = "2024-01-01"
#harvest_date モデル終了日
max_duration = "300"
#モデルを動かす期間の最大値(日)

#soilデータ
soil = CABOFileReader("ec3.soil")

#cropdデータ，yamlフォルダを参照
cropd = YAMLCropDataProvider(fpath=r"yaml")
cropd.set_active_crop('tomato','tomato_01')

weathertimeseries = create_(g_prec_no,g_block_no,g_start_date,g_end_date,plantdata_excel_2hour,chamber_explanatory,nl1)


"""PCSEで使用できる形式にまとめる"""
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
agromanagement = yaml.load(yaml_agro,Loader=yaml.Loader)
wofost = tomatomato(parameterprovider,weatherdataprovider, agromanagement, weathertimeseries,cropinitiallist,modelkinds)

wofost.run_till_terminate()
output = wofost.my_get_output("出力結果用path")
