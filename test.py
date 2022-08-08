#%%
from pcse.crop import phenology,leaf_dynamics,respiration,partitioning,wofost7
# from  pcse.crop.phenology import DVS_Phenology as Phenology
from pcse.base import SimulationObject , VariableKiosk, AncillaryObject,StatesTemplate,WeatherDataProvider
from pcse.traitlets import Float, Integer, Instance
from datetime import date
# from pcse.crop import DVS_Phenology
import numpy as np
import copy
from pcse.fileinput import ExcelWeatherDataProvider
#%%




