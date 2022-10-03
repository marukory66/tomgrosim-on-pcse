#%%
import sys, os
import matplotlib
import matplotlib.pyplot as plt
import pandas as pd
import pcse
from pcse.fileinput import CABOFileReader
from pcse.util import WOFOST72SiteDataProvider
from pcse.base import ParameterProvider
from pcse.fileinput import YAMLAgroManagementReader
from pcse.fileinput import ExcelWeatherDataProvider,PCSEFileReader,CABOWeatherDataProvider
from models import sample 
#%%
# Directory setting
# wd = "/Users/naofujiuchi/Documents/Diary/research/crop_simulation_model"
soil = PCSEFileReader("C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse/test_data/lintul3_springwheat.soil")
site = PCSEFileReader("C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse/test_data/lintul3_springwheat.site")
crop_hujiuchi = PCSEFileReader("C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse/SUG0601.crop")
parameters = ParameterProvider(sitedata=site, soildata=soil, cropdata=crop_hujiuchi)
weatherfile = os.path.join("C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse/nl1.xlsx")
agromanagement_file = os.path.join("C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse/test_data/sugarbeet_calendar.agro")
sited = WOFOST72SiteDataProvider(WAV=10, CO2=360) # site parameters
agromanagement = YAMLAgroManagementReader(agromanagement_file) # agromanagement
# Daily environmental conditions
# Solar radiation, air temperature, vapor pressure, wind speed, precipitation, and snow depth.
wdp = ExcelWeatherDataProvider(weatherfile) # daily weather observation
#%%
# Run simulation
#sample部分でモデルを指定
wofsim = sample(parameters, wdp, agromanagement)
wofsim.run_till_terminate()
df_results = pd.DataFrame(wofsim.get_output())
df_results = df_results.set_index("day")

#%%

A = [[0,0,0,0,0,0,0]]
B = [0,0,0]

for index in range(20):
    A.append(B)
# print(A)

#%%
import datetime as dt
lists = [[i for i in range(1,8)]]
print(lists)

print(lists)

# %%
import numpy as np
import datetime 
import pandas as pd
start = datetime.datetime.strptime("2021-12-1", "%Y-%m-%d")
date_generated = pd.date_range(start, periods=6,freq="3d")
date_generated = [str(i) for i in date_generated]
# print(np.array(str(date_generated)).reshape(2,3).tolist())
print(date_generated.strftime("%Y-%m-%d"))

# %%
from datetime import datetime, timedelta
import numpy as np

date_list = [datetime(2020, 1, 25) + timedelta(days=i) for i in range(7)]
date_list = [d.strftime("%Y-%m-%d") for d in date_list]
da = date_list[-1]
# print(da)
# date_lists = [str(da) + timedelta(days=i) for i in range(1,180,3)]
# print(date_lists)



# 日付のリスト生成()
# date_list = [datetime(2020, 1, 25) + timedelta(days=i) for i in range(20)]
# # 文字列に変換
# date_str_list = [d.strftime("%Y-%m-%d") for d in date_list]
# print(np.array(date_str_list).reshape([20,3]))


# %%
# lists = [[0,0,0,0,0,0,0]]
# for index in range(20):
#     lists.append([0,0,0])
start = datetime.datetime.strptime("2021-12-1", "%Y-%m-%d")
date_generated = pd.date_range(start, periods=60,freq="3d")
date_generated = [str(i) for i in date_generated]
print(np.array(date_generated).reshape([3,20]))
print(date_generated.strftime("%Y-%m-%d"))


# %%