#%%
# Naomichi Fujiuchi (naofujiuchi@gmail.com), April 2022
# This is a derivative work by Fujiuchi (GNU GPL license) from the original work PCSE by Allard de Wit (allard.dewit@wur.nl) (EUPL license).
# import matplotlib.pyplot as plt
# import pandas as pd
# import pcse
# from pcse.models import Wofost72_WLP_FD
# from pcse.fileinput import CABOFileReader,YAMLCropDataProvider,CSVWeatherDataProvider
# from pcse.db import NASAPowerWeatherDataProvider
# from pcse.util import WOFOST72SiteDataProvider
# from pcse.base import ParameterProvider
# from models import tomatomato
# import glob
# import os, sys
# from urllib.request import urlopen
# from urllib.error import URLError
# import pickle
# import yaml
# from pcse.base import MultiCropDataProvider
# from pcse import exceptions as exc
# from pcse import settings
# from pcse.util import version_tuple
# import datetime
# from create_csv.calc_diffusion_fraction import *
# from create_csv.chamber import pick_up_chamber_data
# from create_csv.assimP import calculate_LPHCUR,LPHCUR
# from create_csv.weather_excel import temperature_outside_chamber
# from create_csv.csv_main import create_
# from input_data.main import _create_input_data

class base_TOMULATION():
    def __init__(self,g_prec_no,g_block_no,g_start_date,g_end_date,plantdata_excel_2hour,chamber_explanatory,weatherfile,cropinitiallist,modelkinds,campaign_start_date,emergence_date,harvest_date,max_duration,output_path):
        self.g_prec_no = g_prec_no
        self.g_block_no = g_block_no
        self.g_start_date = g_start_date
        self.g_end_date = g_end_date
        self.plantdata_excel_2hour = plantdata_excel_2hour
        self.chamber_explanatory = chamber_explanatory
        self.weatherfile = weatherfile
        self.cropinitiallist = cropinitiallist
        self.modelkinds = modelkinds
        self.campaign_start_date = campaign_start_date
        self.emergence_date = emergence_date
        self.harvest_date = harvest_date
        self.max_duration = max_duration
        self.output_path = output_path

    def main(self):

        nl1 = os.getcwd()+"/nl1.xls"

        #1日ごとの気象データを与えるためdf.csvのpath要編集 df.csv
        weatherfile = self.weatherfile
        #glob.glob(C:/Users/・・・/inpt_data/*.csvで指定して各種初期値を取得する
        cropinitiallist = _create_input_data(glob.glob(self.cropinitiallist))
        #モデルの種類を選択　Actual_measurement or Predict
        modelkinds = self.modelkinds

        campaign_start_date = self.campaign_start_date
        emergence_date = self.emergence_date
        #emergence_date モデル開始日
        harvest_date = self.harvest_date
        #harvest_date モデル終了日
        max_duration = self.max_duration
        #モデルを動かす期間の最大値(日)
        output_path = self.output_path


        soil = CABOFileReader(os.getcwd()+"/ec3.soil")
        cropd = YAMLCropDataProvider(os.getcwd()+"/yaml")
        cropd.set_active_crop('tomato','tomato_01')
        #圃場の気象データ取得
        weathertimeseries = create_(self.g_prec_no,self.g_block_no,self.g_start_date,self.g_end_date,self.plantdata_excel_2hour,self.chamber_explanatory,nl1)

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
        agromanagement = yaml.load(yaml_agro,Loader=yaml.Loader)
        wofost = tomatomato(parameterprovider,weatherdataprovider, agromanagement, weathertimeseries,cropinitiallist,modelkinds)

        wofost.run_till_terminate()
        output = wofost.my_get_output(output_path)
