#%%
# %matplotlib inline
import sys, os
import matplotlib
# matplotlib.style.use("ggplot")
import matplotlib.pyplot as plt
import pandas as pd

import pcse
from pcse.fileinput import CABOFileReader
from pcse.util import WOFOST72SiteDataProvider
from pcse.base import ParameterProvider
from pcse.fileinput import YAMLAgroManagementReader
from pcse.fileinput import ExcelWeatherDataProvider,PCSEFileReader,CABOWeatherDataProvider
# from pcse.models import Wofost72_WLP_FD, Wofost72_P
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
# Figures
fig, axes = plt.subplots(nrows=2, ncols=2, figsize=(12,10))
for var, ax in zip(["DVS", "TAGP", "LAI", "SM"], axes.flatten()):
    ax.plot_date(df_results.index, df_results[var], 'b-')
    ax.set_title(var)
fig.autofmt_xdate()

#%%
# list_DOEF = [[0 for i in range(3)] for j in range(5)]

list_DOEF = []
i = 0
for index in range(15):
    listA = []
    print("a",index)
    while i <= 2:
        print("1",i)
        listA.append([i][index])
        list_DOEF.append(listA)
        i += 1
print(list_DOEF)