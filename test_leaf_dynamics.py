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
"""
register_variableが出来ていない？
"""
#%%
from leaf_dynamics import TOMGROSIM_Leaf_Dynamics as TOMGRO
#%%

kiosk = VariableKiosk() 
id0 = 0
kiosk.register_variable(oid = id0,varname= "DOHLI", type="S", publish=True)
print(kiosk)
#%%
weatherfile = os.path.join("C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse/nl1.xlsx")
wdp = ExcelWeatherDataProvider(weatherfile) # daily weather observation
drv = wdp(date(2007,7,3))
print(drv)
print(type((drv.TMAX + drv.TMIN)/2))

#%%
soil = PCSEFileReader("C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse/test_data/lintul3_springwheat.soil")
site = PCSEFileReader("C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse/test_data/lintul3_springwheat.site")
crop = PCSEFileReader("C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse/test_data/lintul3_springwheat.crop")

parvalues = ParameterProvider(sitedata=site, soildata=soil, cropdata=crop)
print(parvalues)
kiosk.set_variable(id0, varname = "DOHLI", value = 1)
print(kiosk)
#%%parvalues=parvalues
TOMGRO = TOMGRO(day=date(2007,7,3), kiosk=kiosk,)

TOMGRO.calc_rates(day=date(2007,7,3), drv=drv,kiosk=kiosk)


#%%











lists = [[0.1 for i in range(4)] for j in range(5)]
list_DOHL = copy.deepcopy(lists)
DOHF = list_DOHL
print(type(DOHF[1][2]))






