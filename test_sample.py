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
crop_hujiuchi = PCSEFileReader("C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse/test_data/SUG0601_modified.crop")
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
A = [[0,0,0,0,0,0,0]]
li = lambda i:i.append([0,0,0],A)
print(li)

