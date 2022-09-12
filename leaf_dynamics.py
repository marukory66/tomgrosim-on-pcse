# -*- coding: utf-8 -*-
#%%
# Naomichi Fujiuchi (naofujiuchi@gmail.com), April 2022
# This is a derivative work by Fujiuchi (GNU GPL license) from the original work PCSE by Allard de Wit (allard.dewit@wur.nl) (EUPL license).
from datetime import datetime as dt
from math import exp
from collections import deque
from array import array

from pcse.traitlets import Float, Int, Instance
from pcse.decorators import prepare_rates, prepare_states
from pcse.util import limit, AfgenTrait
from pcse.base import ParamTemplate, StatesTemplate, RatesTemplate, \
     SimulationObject
from pcse import signals
from pcse.fileinput import ExcelWeatherDataProvider,PCSEFileReader,CABOWeatherDataProvider
import copy
import os
from datetime import date
#%%
class TOMGROSIM_Leaf_Dynamics(SimulationObject):

    class Parameters(ParamTemplate):
        PD  = Float(-99.)
        POLA = Float(-99.)
        POLB = Float(-99.)
        POLC = Float(-99.)
        FRPET = Float(-99.)
        SLAMAX = Float(-99)
        SLAMIN  = Float(-99.)
        BETAT  = Float(-99.)
        BETAC  = Float(-99.)

    class StateVariables(StatesTemplate):
        LV     = Instance(list)
        SLA    = Instance(list)
        LA = Instance(list)
        LAI    = Float(-99.) # Total leaf area of living leaves
        WLV    = Float(-99.) # Total leaf weight of living leaves
        DWLV   = Float(-99.) # Total weight of harvested leaves
        TWLV   = Float(-99.) # Total weight of all the leaves (including harvested leaves)
        DOHL = Instance(list) # Day of harvest of leaves (removing lower leaves)
        ACL = Instance(list) # Actual expantion rate of each leaf
        GRLV  = Instance(list)
        SSLA = Float(-99.) # Structrual SLA of each leaf
        POL = Instance(list) # Potential expansion rate of each leaf
        LVAGE  = Instance(list)
        PGRLV = Instance(list) # Potential growth rate of leaves
        MPGRLV = Instance(list) # Maximum potential growth rate of leaves (without any loss of growth)


    class RateVariables(RatesTemplate):
        pass

    def initialize(self, day, kiosk, parvalues):
        
        #　はかきする日が入ったlist
        lists = [[1 for i in range(3)] for j in range(20)]
        list_DOHL = copy.deepcopy(lists)
        list_DOHL[0][0] = list_DOHL
        DOHL = list_DOHL

        list_LV = copy.deepcopy(lists)
        # list_LV[0][0] = list_LV
        LV = list_LV

        list_SLA = copy.deepcopy(lists)
        list_SLA[0][0] = list_SLA
        SLA = list_SLA

        list_LA = copy.deepcopy(lists)
        # list_LA[0][0] = list_LA
        LA = list_LA

        # 以下rate
        list_PGRLV = copy.deepcopy(lists)
        # list_PGRLV[0][0] = list_PGRLV
        PGRLV = list_PGRLV
        
        ACL = copy.deepcopy(lists)
        POL = copy.deepcopy(lists)
        LVAGE = copy.deepcopy(lists)
        PGRLV = copy.deepcopy(lists)
        MPGRLV = copy.deepcopy(lists)
        GRLV = copy.deepcopy(lists)
        SSLA = 1





        self.kiosk  = kiosk
        self.params = self.Parameters(parvalues)

        # CALCULATE INITIAL STATE VARIABLES
        params = self.params
        
     

    

        # Initial leaf biomass, leaf area, and leaf age
        # LV = params.LVI # Dry weights of the leaves that have not generated yet are 0.
        # LA = params.LAI # List of initial leaf area
        # SLA = params.SLAI  # SLAs of the leaves that have not generated yet are 0.
        # DOHL = params.DOHLI
        WLV = 0.
        DWLV = 0.
        LAI = 0.
        for i in range(0, len(LV)):
            for j in range(0, len(LV[i])):
                if DOHL[i][j] != None: # Harvested = Dead
                    # DWLV += LV[i][j]
                    DWLV = LV[i][j]
                    
                
                else: # Not harvested yet = living
                    WLV += LV[i][j]
                    LAI += LA[i][j]
        TWLV = WLV + DWLV

        # Initialize StateVariables object
        self.states = self.StateVariables(kiosk, publish=["LV","LA","SLA","LAI","TWLV","WLV","DWLV","DOHL","ACL","SSLA"],
                                          LV=LV, LA=LA, SLA=SLA,ACL=ACL,LVAGE=LVAGE,PGRLV=PGRLV,MPGRLV=MPGRLV,POL=POL,
                                          LAI=LAI, WLV=WLV, DWLV=DWLV, TWLV=TWLV,GRLV=GRLV,SSLA=SSLA,
                                          DOHL=DOHL)
        
        # self.states = self.StateVariables(kiosk, publish=["PGRLV ","LV","LA","SLA","LAI","TWLV","WLV","DWLV","DOHL"],
        #                                   LV=LV, LA=LA, SLA=SLA, PGRLV=PGRLV, 
        #                                   LAI=LAI, WLV=WLV, DWLV=DWLV, TWLV=TWLV, 
        #                                   DOHL=DOHL)



        # self.rates = self.RateVariables(kiosk, publish=["GRLV","POL","ACL","SSLA","LVAGE","PGRLV","MPGRLV"], 
        #                                 SSLA=None, GRLV=None, POL=None, ACL=None, LVAGE=None, PGRLV=None, MPGRLV=None)
        self.rates = self.RateVariables(kiosk)



    @prepare_rates
    def calc_potential(self, day, drv):
        r = self.rates
        p = self.params
        k = self.kiosk

        # List of harvested (0: harvested, 1: not yet harvested)
        LOH = k.DOHL
        for i in range(0, len(k.DOHL)):
            for j in range(0, len(k.DOHL[i])):
                if k.DOHL[i][j] == None:
                    LOH[i][j] = 1
                else: 
                    LOH[i][j] = 0

        # Leaf age
        r.LVAGE = k.DOEL
        for i in range(0, len(k.DOEL)):
            for j in range(0, len(k.DOEL[i])):
                if k.DOEL[i][j] != None:
                    # print("DOEL",k.DOEL[i][j])
                    # DOEL_days = dt.strptime(k.DOEL[i][j],"%Y/%m/%d" )
                    # # print(type(k.DOEL[i][j]))
                    # age_days = day - DOEL_days.date()

                    # r.LVAGE[i][j] = age_days.days
                    r.LVAGE[i][j] = k.DOEL[i][j]
                else:
                    r.LVAGE[i][j] = 0            

        # List of potential leaf expansion rate of each leaf
        # The first derivative of a Gompertz function relating area of growing leaves to time from leaf appearance (Berin, 1993, Ph.D. thesis) 
        # yields the potential area expansion rate of a leaf (Heuvelink and Bertin, 1994, J. Hort. Sci,)
        
        #直置き後で直す
        weatherfile = os.path.join("C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse/nl1.xlsx")
        wdp = ExcelWeatherDataProvider(weatherfile) # daily weather observation
        drv = wdp(day)
        # drv = wdp(date(2007,7,3))
        
        drv.TEMP = ((drv.TMAX + drv.TMIN)/2)
        if drv.TEMP <= 28:
            FTEMP = 1.0 + 0.0281 * (drv.TEMP - 28)
        else:
            FTEMP = 1.0 - 0.0455 * (drv.TEMP - 28)
        #　記載が無いため仮置き 400固定でOK
        drv.CO2 = 400
        FCO2 = 1 + 0.003 * (drv.CO2 - 350)
        
        r.POL = [list(map(lambda x: p.PD * FTEMP * FCO2 * p.POLA * p.POLB * exp(-p.POLB * (1 - p.POLC)) * exp(-exp(-p.POLB * (1 - p.POLC))), row)) for row in r.LVAGE] # p.PD: plant density
        # r.POL = [list(map(lambda x: p.PD * FTEMP * FCO2 * p.POLA * p.POLB * exp(-p.POLB * (x - p.POLC)) * exp(-exp(-p.POLB * (x - p.POLC))), row)) for row in r.LVAGE] 
        r.POL = [[a * b for a, b in zip(*rows)] for rows in zip(r.POL, LOH)] # Set POL of harvested leaves at 0.


        # Structural SLA (sSLA)
        # sSLA calculation of TOMGRO (Jones et al., 1991, Transaction of the ASAE). Parameter values of (Heuvelink and Bertin, 1994, J. Hort. Sci.) were used.
        #全日射(IRRAD)を光合成有効放射(PAR)に変換して使用
        drv.PAR = drv.IRRAD*1000*2.285*10**(-6)
        
        # drv.PAR = 1
        r.SSLA = (p.SLAMAX + (p.SLAMAX - p.SLAMIN) * exp(-0.471 * drv.PAR)) / (1 + p.BETAT * (24 - drv.TEMP)) / (1 + p.BETAC * (drv.CO2 - 350))

        # Potential growth rates of leaves (PGRLV) and fruits (PGRFR) that are not harvested yet.
        # Maximum potential growth rate of leaves (MPGRLV) is defined by the day's POL and SSLA
        # Potential growth rate of leaves (PGRLV) is MPGRLV * CAF.
        # The cumulative adaptation factor (CAF) is a state variable calculated in wofost.py
        r.MPGRLV = [list(map(lambda x: x / r.SSLA, row)) for row in r.POL]
        r.MPGRLV = [list(map(lambda x: (1 + p.FRPET) * x, row)) for row in r.MPGRLV] # Include petiole (partitioning ratio of dry matter, petiold:leaf = FRPET:1)
        r.PGRLV = [list(map(lambda x: k.CAF * x, row)) for row in r.MPGRLV]


    @prepare_rates
    # def calc_rates(self, day, drv):
    def calc_rates(self, day, drv ):
        r = self.rates
        p = self.params
        k = self.kiosk
        
        list_PGRLV = [[0 for i in range(3)] for j in range(20)]
        list_PGRLV[0][0] = list_PGRLV
        PGRLV = list_PGRLV
        
        # PGRLV =  initialize.PGRLV

        # Growth rate leaves

        """試しに数値を直置き"""
        # r.GRLV = [list(map(lambda x: k.DMI * x / k.TPGR, row)) for row in k.PGRLV] # List of dry mass partitioned to each leaf depending on its potential growth rate (PGRLV)        
        k.GRLV = [list(map(lambda x: 1, row)) for row in PGRLV]
        
        # ↓これは，mapの確認用なので不必要　
        # r.DVRF =  [list(map(lambda x: self._dev_rate_fruit(drvTEMP, x), row)) for row in s.DVSF]
        
        # Actual leaf expansion rate
        # r.ACL = [list(map(lambda x: x / (1 + p.FRPET), row)) for row in r.GRLV] # Exclude petiole from the growth rate of leaf
        k.ACL = [list(map(lambda x: x / (1 + 1), row)) for row in k.GRLV] # Exclude petiole from the growth rate of leaf
        k.ACL = [list(map(lambda x: x * k.SSLA, row)) for row in k.ACL] # Convert dry mass increase to leaf expansion
        # r.ACL = [list(map(lambda x: x * r.SSLA, row)) for row in r.ACL] # Convert dry mass increase to leaf expansion
        
        
    @prepare_states
    def integrate(self, day, delt=1.0):

        p = self.params
        r = self.rates
        s = self.states
        k = self.kiosk

        # # Update leaf biomass states
        # GRLVをleaf_dynamicsのcalc_ratesで計算後→publish
        k.GRLV = [[0 for i in range(3)] for j in range(20)]
        print("AA",k.GRLV)
        print("aaa",s.LV)
        s.LV = list(map(lambda l1, l2: [sum(x) for x in zip(l1, l2)], s.LV, k.GRLV)) 
        # s.LV = list(map(lambda l1, l2: [sum(x) for x in zip(l1, l2)], s.LV, r.GRLV)) 

        
        # Update leaf area
        s.LA = list(map(lambda l1, l2: [sum(x) for x in zip(l1, l2)], s.LA, k.ACL))
        
        # s.LA = list(map(lambda l1, l2: [sum(x) for x in zip(l1, l2)], s.LA, r.ACL))


        # Update leaf SLA
        s.SLA = [[a / b for a, b in zip(*rows)] for rows in zip(s.LA, s.LV)]

        # Update total leaf biomass
        s.WLV = 0.
        s.DWLV = 0.
        s.LAI = 0.
        for i in range(0, len(s.LV)):
            for j in range(0, len(s.LV[i])):
                # DOHL[i][j] != None: already harvested (= dead), DOHL[i][j] == None: not harvested yet (= living).
                if s.DOHL[i][j] != None:
                    s.DWLV += s.LV[i][j]
                else:
                    s.WLV += s.LV[i][j]
                    s.LAI += s.LA[i][j]
        s.TWLV = s.WLV + s.DWLV

        # Harvest scheme for updating DOHL
        # DOHL ... If the development stage (DVSF) of the 1st fruit of the truss becomes over 0.8, then the leaves on the truss will be removed.
        for i in range(0, len(s.DOHL)):
            for j in range(0, len(s.DOHL[i])):
                if s.DOHL[i][j] == None and k.DVSF[i][0] >= 0.8:
                    s.DOHL[i][j] = day
