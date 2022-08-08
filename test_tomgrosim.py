#%%
from pcse.crop import phenology,leaf_dynamics,respiration,partitioning,wofost7
# from  pcse.crop.phenology import DVS_Phenology as Phenology
from pcse.base import SimulationObject , VariableKiosk, AncillaryObject,StatesTemplate,WeatherDataProvider,ParameterProvider
from pcse.traitlets import Float, Integer, Instance
from datetime import date
# from pcse.crop import DVS_Phenology
import numpy as np
import copy
from pcse.fileinput import ExcelWeatherDataProvider,PCSEFileReader,CABOWeatherDataProvider

#%%
from tomgrosim import Tomgrosim

#%%
# weatherfile = os.path.join(data_dir, 'meteo', 'nl1.xls')

weatherfile = os.path.join("C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse/nl1.xlsx")
wdp = ExcelWeatherDataProvider(weatherfile) # daily weather observation

drv = wdp(date(2007,7,3))
print(drv)
print(type((drv.TMAX + drv.TMIN)/2))
kiosk = VariableKiosk()
# print(type(drvTEMP))
#%%
soil = PCSEFileReader("C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse/test_data/lintul3_springwheat.soil")
site = PCSEFileReader("C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse/test_data/lintul3_springwheat.site")
# crop = PCSEFileReader("C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse/test_data/lintul3_springwheat.crop")
crop_hujiuchi = PCSEFileReader("C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse/test_data/SUG0601_modified.crop")
parvalues = ParameterProvider(sitedata=site, soildata=soil, cropdata=crop_hujiuchi)

#%%
weatherfile = os.path.join("C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse/nl1.xlsx")
wdp = ExcelWeatherDataProvider(weatherfile) # daily weather observation
# print(type(2007,7,3))-
drv = wdp(date(2007,7,3))


TOMGRO=Tomgrosim(day=date(2007,7,3), kiosk=kiosk,parvalues = parvalues)

TOMGRO.integrate(day=date(2007,7,3))



# TOMGRO.calc_rates(kiosk=kiosk,day=date(2007,7,3), drv=drv,parvalues = parvalues)


#%%

from math import exp
MPGRFR = [list(map(lambda x: 1.0 * 1.0 * 1.0 * (1 + exp(-1.0*(x - 1.0)))**(1/(1-1.1)) / ((1.1-1) * (exp(1.0 * (x - 1.0)) + 1)), row)) for row in [[2,3,4],[2,3,4]]] # p.PD: plant density
print(MPGRFR)