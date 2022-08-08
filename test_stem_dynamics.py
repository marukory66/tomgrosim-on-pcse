#%%
import sys, os
from pcse.crop import phenology,leaf_dynamics,respiration,partitioning,wofost7
# from  pcse.crop.phenology import DVS_Phenology as Phenology
from pcse.base import SimulationObject , VariableKiosk, AncillaryObject,StatesTemplate,WeatherDataProvider,ParameterProvider
from pcse.traitlets import Float, Integer, Instance
from datetime import date
# from pcse.crop import DVS_Phenology
import numpy as np
import copy
from sqlalchemy import create_engine, MetaData, Table
from pcse.fileinput import ExcelWeatherDataProvider,  PCSEFileReader,CABOWeatherDataProvider
#%%
from stem_dynamics import Simple_Stem_Dynamics 
#%%
weatherfile = os.path.join("C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse/nl1.xlsx")
wdp = ExcelWeatherDataProvider(weatherfile) # daily weather observation

drv = wdp(date(2007,7,3))
print(drv)
print(type((drv.TMAX + drv.TMIN)/2))
kiosk = VariableKiosk()
#%%
soil = PCSEFileReader("C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse/test_data/lintul3_springwheat.soil")
site = PCSEFileReader("C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse/test_data/lintul3_springwheat.site")
crop = PCSEFileReader("C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse/test_data/lintul3_springwheat.crop")

parvalues = ParameterProvider(sitedata=site, soildata=soil, cropdata=crop)


#%%
Simple_R = Simple_Stem_Dynamics(day=date(2007,7,3), kiosk=kiosk,parameters = parvalues)
Simple_R.calc_rates(day=date(2007,7,3), drv=drv,kiosk=kiosk)

