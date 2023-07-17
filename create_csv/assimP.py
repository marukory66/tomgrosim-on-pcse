#%%
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

# assim_calculation = "C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse_pypl/df.csv"
# df_assim_calculation = pd.read_csv(assim_calculation)

def calculate_LPHCUR(df_assim_calculation):
  df_ = pd.DataFrame(columns=["EFF","PGMAX"])
  for i1,i in enumerate(range(len(df_assim_calculation)-1)):
    tmp = df_assim_calculation.iloc[i1]
    TLEAF = tmp["Temperature inside chamber"]
    CO2AIR = tmp["CO2 concentration air sampling average"]
    EFF_,PGMAX_ = LPHCUR(TLEAF,CO2AIR,"g")
    df_.loc[i1] = [EFF_,PGMAX_]
  df_assim_calculation = pd.concat([df_assim_calculation,df_],axis=1)
  return df_assim_calculation
