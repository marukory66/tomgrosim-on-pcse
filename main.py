#%%
import os, sys
import matplotlib
# matplotlib.style.use("ggplot")
import matplotlib.pyplot as plt
import pandas as pd
import yaml
import pcse
from pcse.models import Wofost72_WLP_FD
from pcse.fileinput import CABOFileReader, YAMLCropDataProvider
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
"""PCSEが使用できる形式にまとめる"""
cropd = YAMLCropDataProvider(fpath=r"C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse_pypl/yaml")
#トマト用なのでトマトは確定として，複数verを用意してcropd.set_active_cropでtomato_01，tomato_02みたいな感じで指定してもらう
cropd.set_active_crop('tomato','tomato_01')
soil = CABOFileReader("C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse/test_data/ec3.soil")
site = WOFOST72SiteDataProvider(WAV=10,CO2=360)
parameterprovider = ParameterProvider(soildata=soil, cropdata=cropd, sitedata=site)

from pcse.fileinput import ExcelWeatherDataProvider


"""これらの数字をコマンドから持ってこれるようにする"""
campaign_start_date = "2019-12-07"
emergence_date = "2019-12-25"
harvest_date = "2020-03-20"
max_duration = "300"



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
agro = yaml.safe_load(yaml_agro)



weatherfile = ("C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse_pypl/df.xls")
weatherdataprovider = ExcelWeatherDataProvider(weatherfile)
agromanagement = yaml.load(yaml_agro,Loader=yaml.Loader)
wofost = tomatomato(parameterprovider,weatherdataprovider, agromanagement)
wofost.run_till_terminate()
output = wofost.get_output()
df = pd.DataFrame(output).set_index("day")
df.tail()
