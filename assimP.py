# %%
import csv
import pandas as pd
from datetime import datetime
from datetime import date
asai_2hour = "C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse/asai_plantation_data/asai_pi01_20191023_2hour.csv"
df = pd.read_csv(asai_2hour)
LPHCUR_df = df[["Date","Temperature inside chamber","CO2 concentration air sampling average"]]
LPHCUR_df = LPHCUR_df.loc[750:2669]
LPHCUR_df.to_csv("C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse/asai_plantation_data/TREAF_CO2AIR.csv")

# %%
#Rをpythonに書き換えここに二つとも記載
#unit(単位)によって計算方法を切り替え
from scipy.interpolate import interp1d
import pandas as pd

def LPHCUR(TLEAF,CO2AIR,unit):
  RS = 50 # [s m-1]
  RB = 100 # [s m-1]
  Q10RD = 2.0
  
  if unit == "g":
    EFF0 = 0.017 # [mgCO2 J-1]
    RD20 = 0.05 # [mgCO2 m-2 s-1]
    GCT_X = [0, 5, 15, 25, 40, 100]
    GCT_Y = [0, 0, 0.004, 0.004, 0, 0]
    PMMT_X = [0, 5, 15, 25, 40, 100]
    PMMT_Y = [0, 0, 2, 2, 0, 0]
  
  elif unit == "mol":
    EFF0 = 0.084 # [molCO2 mol-1photon]
    RD20 = 1.136 # [µmolCO2 m-2 s-1]
    GCT_X = [0, 5, 15, 25, 40, 100]
    GCT_Y = [0, 5, 15, 25, 40, 100]
    PMMT_X = [0, 5, 15, 25, 40, 100]
    PMMT_Y = [0, 0, 45, 45, 0, 0]

  GC_1d = interp1d(GCT_X, GCT_Y)
  GC = GC_1d(TLEAF)
  if GC < 0.00001:
    RC = 3 * (10**30)
  else:
    RC = 1 / GC
  PMM_1d = interp1d(PMMT_X, PMMT_Y)
  PMM = PMM_1d(TLEAF)
  GAMMA = 42.7 + 1.68 * (TLEAF - 25) + 0.012 * (TLEAF - 25)**2
  CO2 = max(CO2AIR,GAMMA)
  EFF_ = EFF0 * (CO2 - GAMMA) / (CO2 + 2 * GAMMA)
  if unit == "g":
    ALPHA = 1.8
  elif unit == "mol":
    ALPHA = 41.6
  PNC = ALPHA * (CO2 - GAMMA) / (1.36 * RB + 1.6 * RS + RC)
  PNMAX = min(PNC, PMM)
  RD = RD20 * Q10RD**(0.1 * (TLEAF - 20))
  PGMAX_ = PNMAX + RD

  return EFF_,PGMAX_


assim_calculation = "C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse/assim_calculation.csv"
df_assim_calculation = pd.read_csv(assim_calculation)


date_list = df_assim_calculation["date"].values.tolist() 
# for i in range(len(date_list)):
#   tmp_date_list = date_list[i]
#   date_list[i] = tmp_date_list[0:10]
date_list = list(dict.fromkeys(date_list))

df = pd.DataFrame(columns=["EFF","PGMAX"]) 
print(df)
for i1,i in enumerate(range(len(date_list))):
  for i2,j in enumerate(range(1,24,2)):
    tmp = df_assim_calculation.query('date == @date_list[@i] and hour ==@j')
    tmp_TLEAF = tmp["Temperature inside chamber"]
    TLEAF = tmp_TLEAF.iloc[-1]
    tmp_CO2AIR = tmp["CO2 concentration air sampling average"]
    CO2AIR = tmp_CO2AIR.iloc[-1]
    EFF_,PGMAX_ = LPHCUR(TLEAF,CO2AIR,"g")
    ii = i1*12 + i2
    df.loc[ii] = [EFF_,PGMAX_]
    print(ii)
df_assim_calculation = pd.concat([df_assim_calculation,df],axis=1)
# print(df_assim_calculation)
df_assim_calculation.to_csv('C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse/df_assim_calculation(EFF,PGMAX).csv')

# %%
import math
def ASSIMR(EFF, PGMAX, LAI, SINELV, PARDIR, PARDIF):
  REFGR = 0.5
  SCP = 0.15
  KDIFBL = 0.8
  KDIF = 0.72
  XGAUS3 = [0.112702, 0.5, 0.887298]
  WGAUS3 = [0.277778, 0.444444, 0.277778]
  SINEL = max(0.02, SINELV)
  REFL = (1 - (1 - SCP)**(1/2)) / (1 + (1 - SCP)**(1/2))
  REFPD = REFL * 2 / (1 + 1.6 * SINEL)
  CLUSTF = KDIF / (KDIFBL * (1 - SCP)**(1/2))
  KDIRBL = (0.5 / SINEL) * CLUSTF
  KDIRT = KDIRBL * (1 - SCP)**(1/2)
  T1 = math.exp(-KDIF * LAI)
  T2 = math.exp(-KDIRT * LAI)
  T3 = T1
  CORR1 = (REFL - REFGR) / (REFGR - 1 / REFL) * T1**2
  CORR2 = -REFPD**2 * T2**2
  CORR3 = -REFL**2 * T3**2
  RE1 = (REFL + CORR1 / REFL) / (1 + CORR1)
  RE2 = (REFPD + CORR2 / REFPD) / (1 + CORR2)
  RE3 = (REFL + CORR3 / REFL) / (1 + CORR3)
  TE1 = T1 * (REFL**2 - 1) / (REFL * REFGR - 1) / (1 + CORR1)
  TE2 = T2 * (1 - REFPD**2) / (1 + CORR2)
  TE3 = T3 *(1 - REFL**2) / (1 + CORR3)
  PHIU = REFGR * PARDIR * TE2 / (1 - RE3 * REFGR)
  PGROS = 0
  for i in range(0,3):
    LAIC = LAI * XGAUS3[i]
    PARLDF = (1 - REFL) * KDIF * (PARDIF * (math.exp(-KDIF * LAIC) + CORR1 * math.exp(KDIF * LAIC) / REFL) / (1 + CORR1) + PHIU * (math.exp(KDIF * (LAIC - LAI)) + CORR3 * math.exp(KDIF * (LAI - LAIC)) / REFL) / (1 + CORR3))
    PARLT = (1 - REFPD) * PARDIR * KDIRT * (math.exp(-KDIRT * LAIC) + CORR2 * math.exp(KDIRT * LAIC) / REFPD) / (1 + CORR2)
    PARLDR = (1 - SCP) * PARDIR * KDIRBL * math.exp(-KDIRBL * LAIC)
    PARLSH = PARLDF + (PARLT - PARLDR)
    PARLPP = PARDIR * (1 - SCP) / SINEL
    FSLLA = CLUSTF * math.exp(-KDIRBL * LAIC)
    ASSSH = PGMAX * (1 - math.exp(-EFF * PARLSH / PGMAX))
    ASSSL = 0
    for j in range(0,3):
      PARLSL = PARLSH + PARLPP * XGAUS3[j]
      ASSSL = ASSSL + PGMAX * (1 - math.exp(-EFF * PARLSL/ PGMAX)) * WGAUS3[j]
    PGROS = PGROS + ((1 - FSLLA) * ASSSH + FSLLA * ASSSL) * WGAUS3[i]
  
  PGROS_ = PGROS * LAI
  return PGROS_

a = ASSIMR(0.0124863093358485,1.44626293512067, 3, 0.519804754, 186.1843667, 15.04639687)
print(a*7200)


# %%

# import pandas as pd
# assim_calculation= "C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse/df_assim_calculation(EFF,PGMAX).csv"
# df_assim_calculation = pd.read_csv(assim_calculation)

# date_list = df_assim_calculation["date"].values.tolist() 
# date_list = list(dict.fromkeys(date_list))
# for d in date_list:
#     print(d)
#     hour = list(df_assim_calculation.query('date == @d and h>0')["hour"])
#     print("hour",hour)
#     for i in hour:
#       tmp = (df_assim_calculation.query('date == @d and hour==@i'))
#       h = tmp["h"]
#       print(tmp["h"].iloc[-1])
#     break







# %%

# asai_2hour = "C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse/asai_plantation_data/asai_pi01_20191023_2hour.csv"
# df = pd.read_csv(asai_2hour)
# LPHCUR_df = df.loc[:,["Temperature inside chamber"]]
# LPHCUR_df = df.loc[750:2669]
# print(LPHCUR_df)
# LPHCUR_df = LPHCUR_df[["Date","Minimum temperature outside chamber","Minimum H2O concentration inside chamber(gram)"]]
# LPHCUR_df.to_csv("C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse/asai_plantation_data/TREAF.csv")

# date_list = LPHCUR_df["Date"].values.tolist() 

# def inc_date(date,purpose):
#   match_dates = []
#   for i in range(len(date)):
#     if purpose in date[i]:
#       match_dates.append(i)
#   return match_dates

# def day_ave_assim(match_dates,TLEAFs,CO2AIRs):
#   EFF = 0
#   PGMAX = 0
#   for i in match_dates:
#     TLEAF = TLEAFs[i]
#     CO2AIR = CO2AIRs[i]
#     a = LPHCUR(TLEAF, CO2AIR, "g")
#     EFF += a[0]
#     PGMAX += a[1]
#   return EFF,PGMAX

# for i in range(len(date_list)):
#   tmp_date_list = date_list[i]
#   date_list[i] = tmp_date_list[0:10]
# date_list = list(dict.fromkeys(date_list))

# for i in range(len(date_list)):
#   match_dates = inc_date(date_list, date_list[i])
#   TLEAFs = LPHCUR_df["Minimum temperature outside chamber"].values.tolist()
#   CO2AIRs = LPHCUR_df["Minimum H2O concentration inside chamber(gram)"].values.tolist()
#   EFF,PGMAX = day_ave_assim(match_dates, TLEAFs, CO2AIRs)
#   day = date_list[i]