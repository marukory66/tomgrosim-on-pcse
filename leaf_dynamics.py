# -*- coding: utf-8 -*-
#%%
# Naomichi Fujiuchi (naofujiuchi@gmail.com), April 2022
# This is a derivative work by Fujiuchi (GNU GPL license) from the original work PCSE by Allard de Wit (allard.dewit@wur.nl) (EUPL license).
from math import exp
from collections import deque
from array import array

from pcse.traitlets import Float, Int, Instance
from pcse.decorators import prepare_rates, prepare_states
from pcse.util import limit, AfgenTrait
from pcse.base import ParamTemplate, StatesTemplate, RatesTemplate, \
     SimulationObject
from pcse import signals
#%%
class TOMGROSIM_Leaf_Dynamics(SimulationObject):

    class Parameters(ParamTemplate):
        LVI = Instance(list) # Initial leaf weights
        LAI = Instance(list) # Initial leafarea
        SLAI = Instance(list) # Initial specific leaf area (SLA) 
        DOHLI = Instance(list)  # Initial data of day of harvest of leaves (removing lower leaves)

    class StateVariables(StatesTemplate):
        LV     = Instance(list)
        SLA    = Instance(list)
        LA = Instance(list)
        LAI    = Float(-99.) # Total leaf area of living leaves
        WLV    = Float(-99.) # Total leaf weight of living leaves
        DWLV   = Float(-99.) # Total weight of harvested leaves
        TWLV   = Float(-99.) # Total weight of all the leaves (including harvested leaves)
        DOHL = Instance(list) # Day of harvest of leaves (removing lower leaves)

    class RateVariables(RatesTemplate):
        GRLV  = Instance(list)
        SSLA = Float(-99.) # Structrual SLA of each leaf
        POL = Instance(list) # Potential expansion rate of each leaf
        ACL = Instance(list) # Actual expantion rate of each leaf
        LVAGE  = Instance(list)
        PGRLV = Instance(list) # Potential growth rate of leaves
        MPGRLV = Instance(list) # Maximum potential growth rate of leaves (without any loss of growth)

    def initialize(self, day, kiosk, parvalues):

        self.kiosk  = kiosk
        self.params = self.Parameters(parvalues)

        # CALCULATE INITIAL STATE VARIABLES
        params = self.params

        # Initial leaf biomass, leaf area, and leaf age
        LV = params.LVI # Dry weights of the leaves that have not generated yet are 0.
        LA = params.LAI # List of initial leaf area
        SLA = params.SLAI  # SLAs of the leaves that have not generated yet are 0.
        DOHL = params.DOHLI
        WLV = 0.
        DWLV = 0.
        LAI = 0.
        for i in range(0, len(LV)):
            for j in range(0, len(LV[i])):
                if DOHL[i][j] != None: # Harvested = Dead
                    DWLV += LV[i][j]
                else: # Not harvested yet = living
                    WLV += LV[i][j]
                    LAI += LA[i][j]
        TWLV = WLV + DWLV

        # Initialize StateVariables object
        self.states = self.StateVariables(kiosk, publish=["LV","LA","SLA","LAI","TWLV","WLV","DWLV","DOHL"],
                                          LV=LV, LA=LA, SLA=SLA, 
                                          LAI=LAI, WLV=WLV, DWLV=DWLV, TWLV=TWLV, 
                                          DOHL=DOHL)
        
        self.rates = self.RateVariables(kiosk, publish=["GRLV","POL","ACL","SSLA","LVAGE","PGRLV","MPGRLV"], 
                                        SSLA=None, GRLV=None, POL=None, ACL=None, LVAGE=None, PGRLV=None, MPGRLV=None)

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
                    age_days = day - k.DOEL[i][j]
                    r.LVAGE[i][j] = age_days.days
                else:
                    r.LVAGE[i][j] = 0            

        # List of potential leaf expansion rate of each leaf
        # The first derivative of a Gompertz function relating area of growing leaves to time from leaf appearance (Berin, 1993, Ph.D. thesis) 
        # yields the potential area expansion rate of a leaf (Heuvelink and Bertin, 1994, J. Hort. Sci,)
        if drv.TEMP <= 28:
            FTEMP = 1.0 + 0.0281 * (drv.TEMP - 28)
        else:
            FTEMP = 1.0 - 0.0455 * (drv.TEMP - 28)
        FCO2 = 1 + 0.003 * (drv.CO2 - 350)
        r.POL = [list(map(lambda x: p.PD * FTEMP * FCO2 * p.POLA * p.POLB * exp(-p.POLB * (x - p.POLC)) * exp(-exp(-p.POLB * (x - p.POLC))), row)) for row in r.LVAGE] # p.PD: plant density
        r.POL = [[a * b for a, b in zip(*rows)] for rows in zip(r.POL, LOH)] # Set POL of harvested leaves at 0.

        # Structural SLA (sSLA)
        # sSLA calculation of TOMGRO (Jones et al., 1991, Transaction of the ASAE). Parameter values of (Heuvelink and Bertin, 1994, J. Hort. Sci.) were used.
        r.SSLA = (p.SLAMAX + (p.SLAMAX - p.SLAMIN) * exp(-0.471 * drv.PAR)) / (1 + p.BETAT * (24 - drv.TEMP)) / (1 + p.BETAC * (drv.CO2 - 350))

        # Potential growth rates of leaves (PGRLV) and fruits (PGRFR) that are not harvested yet.
        # Maximum potential growth rate of leaves (MPGRLV) is defined by the day's POL and SSLA
        # Potential growth rate of leaves (PGRLV) is MPGRLV * CAF.
        # The cumulative adaptation factor (CAF) is a state variable calculated in wofost.py
        r.MPGRLV = [list(map(lambda x: x / r.SSLA, row)) for row in r.POL]
        r.MPGRLV = [list(map(lambda x: (1 + p.FRPET) * x, row)) for row in r.MPGRLV] # Include petiole (partitioning ratio of dry matter, petiold:leaf = FRPET:1)
        r.PGRLV = [list(map(lambda x: k.CAF * x, row)) for row in r.MPGRLV]

    @prepare_rates
    def calc_rates(self, day, drv):
        r = self.rates
        p = self.params
        k = self.kiosk

        # Growth rate leaves
        r.GRLV = [list(map(lambda x: k.DMI * x / k.TPGR, row)) for row in k.PGRLV] # List of dry mass partitioned to each leaf depending on its potential growth rate (PGRLV)        
        # Actual leaf expansion rate
        r.ACL = [list(map(lambda x: x / (1 + p.FRPET), row)) for row in r.GRLV] # Exclude petiole from the growth rate of leaf
        r.ACL = [list(map(lambda x: x * r.SSLA, row)) for row in r.ACL] # Convert dry mass increase to leaf expansion

    @prepare_states
    def integrate(self, day, delt=1.0):

        p = self.params
        r = self.rates
        s = self.states
        k = self.kiosk

        # # Update leaf biomass states
        s.LV = list(map(lambda l1, l2: [sum(x) for x in zip(l1, l2)], s.LV, r.GRLV)) 

        # Update leaf area
        s.LA = list(map(lambda l1, l2: [sum(x) for x in zip(l1, l2)], s.LA, r.ACL))

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
