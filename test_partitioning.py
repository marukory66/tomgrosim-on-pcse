#%%
from pcse.crop import phenology,leaf_dynamics,respiration,partitioning,wofost7
# from  pcse.crop.phenology import DVS_Phenology as Phenology
from pcse.base import SimulationObject , VariableKiosk, AncillaryObject,StatesTemplate,WeatherDataProvider,ParameterProvider
from pcse.traitlets import Float, Integer, Instance
from datetime import date
# from pcse.crop import DVS_Phenology
import numpy as np
import copy
from pcse.fileinput import ExcelWeatherDataProvider,  PCSEFileReader,CABOWeatherDataProvider
#%%
from partitioning import DVS_Partitioning 
#%%

# weatherfile = os.path.join(data_dir, 'meteo', 'nl1.xls')

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

DVS_P = DVS_Partitioning(day=date(2007,7,3), kiosk=kiosk,parvalues=parvalues )
DVS_P.calc_rates(day=date(2007,7,3), drv=drv,kiosk=kiosk)


#%%
sample = [1,2,3,4]
# TMPGRFR = (map(sum, sample)) # Total potential growth rate of all the fruits
# print(TMPGRFR)
a = sum(sample)
print(a)

