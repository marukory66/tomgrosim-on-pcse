#%%
import pandas as pd
import re
from datetime import datetime
from datetime import date as dt
import openpyxl as xl



def temperature_outside_chamber(chamber_explantory,nl1):
    df_chamber_explantory = pd.read_csv(chamber_explantory)
    date = df_chamber_explantory["Date"]
    IRRAD = df_chamber_explantory["Solar.radiation.accu"]
    TMIN = df_chamber_explantory["Temperature.outside.chamber.nightave"]
    TMAX = df_chamber_explantory["Temperature.outside.chamber.dayave"]
    for i in range(len(date)):
        tmp = date[i]
        date[i] = pd.to_datetime(date[i],format='%Y/%m/%d')
        date[i] = date[i].to_pydatetime()

    df_nl1 = pd.read_excel(nl1)

    for i in range(len(date)):
        df_nl1.iloc[11+i,0] = date[i]
        df_nl1.iloc[11+i,1] = IRRAD[i]
        df_nl1.iloc[11+i,2] = TMIN[i]
        df_nl1.iloc[11+i,3] = TMAX[i]
    return df_nl1
