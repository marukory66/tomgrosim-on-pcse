# -*- coding: utf-8 -*-
#%%
# Naomichi Fujiuchi (naofujiuchi@gmail.com), April 2022
# This is a derivative work by Fujiuchi (GNU GPL license) from the original work PCSE by Allard de Wit (allard.dewit@wur.nl) (EUPL license).
from math import exp

from pcse.traitlets import Float, Int, Instance
from pcse.decorators import prepare_rates, prepare_states
from pcse.util import limit
from pcse.base import ParamTemplate, StatesTemplate, RatesTemplate, \
    SimulationObject, VariableKiosk
#%%
class TOMGROSIM_Storage_Organ_Dynamics(SimulationObject):

    class Parameters(ParamTemplate):      
        SPA  = Float(-99.)
        TDWI = Float(-99.)

    class StateVariables(StatesTemplate):
        FD = Instance(list)
        DMC = Instance(list)
        FF = Instance(list)
        DOHF = Instance(list)
        WSO  = Float(-99.) # Weight living storage organs
        DWSO = Float(-99.) # Weight dead storage organs (Cumulative yield (dry mass))
        YWSO = Float(-99.) # Cumulative yield (fresh mass)
        TWSO = Float(-99.) # Total weight storage organs (Dry mass)

    class RateVariables(RatesTemplate):
        GRFR = Instance(list), # Actual growth rate of a fruit
        GRFRF = Instance(list), # Actual growth rate of a fruit on a fresh mass basis
        PGRFR = Instance(list), # Potential growth rate of a fruit
        MPGRFR = Instance(list), # Maximum potential growth rate of a fruit
        SDMC = Float(-99.), # Structural dry matter content of a fruit
        FRAGE = Instance(list) # Age of a fruit [d]
        
    def initialize(self, day, kiosk, parvalues):

        self.params = self.Parameters(parvalues)
        self.kiosk = kiosk
        
        # INITIAL STATES
        params = self.params

        FD = params.FDI # List of dry mass of fruits. Weights of the fruits that have not generated yet are 0.
        DMC = params.DMCI # List of dry matter content (DMC). DMCs of the leaves that have not generated yet are None.
        FF = params.FFI # List of fresh mass of fruits. Weights of the fruits that have not generated yet are 0.
        DOHF = params.DOHFI

        WSO = 0.
        DWSO = 0.
        YWSO = 0.
        for i in range(0, len(FD)):
            for j in range(0, len(FD[i])):
                if DOHF[i][j] != None: # Harvested = Dead
                    DWSO += FD[i][j] # Cumulative yield (dry mass)
                    YWSO += FF[i][j] # Cumulative yield (fresh mass)
                else: # Not harvested yet = living
                    WSO += FD[i][j]
        TWSO = WSO + DWSO # Total dry mass of fruits (both living and dead)

        self.states = self.StateVariables(kiosk, publish=["FD","DMC","FF","DOHF","WSO","DWSO","YWSO","TWSO"],
                                          FD=FD, DMC=DMC, FF=FF, DOHF=DOHF,
                                          WSO=WSO, DWSO=DWSO, YWSO=YWSO, TWSO=TWSO)

        self.rates = self.RateVariables(kiosk, publish=["GRFR","PGRFR","MPGRFR","SDMC","FRAGE"], 
                                        GRFR=None, GRFRF=None, PGRFR=None, MPGRFR=None, SDMC=None, FRAGE=None)

    @prepare_rates
    def calc_potential(self, day, drv):
        r = self.rates
        p = self.params
        k = self.kiosk

        # List of harvested (0: harvested, 1: not yet harvested)
        LOH = k.DOHF
        for i in range(0, len(k.DOHF)):
            for j in range(0, len(k.DOHF[i])):
                if k.DOHF[i][j] == None:
                    LOH[i][j] = 1
                else: 
                    LOH[i][j] = 0

        # Fruit age
        r.FRAGE = k.DOEF
        for i in range(0, len(k.DOEF)):
            for j in range(0, len(k.DOEF[i])):
                if k.DOEF[i][j] != None:
                    age_days = day - k.DOEF[i][j]
                    r.FRAGE[i][j] = age_days.days
                else:
                    r.FRAGE[i][j] = 0

        # List of potential fruit growth rate of each fruit
        # The potential growth rate of a truss (PGR) is given by the first derivative of the Richards growth function (Richards, 1959), 
        # relating fruit dry weight to time after anthesis (Heuvelink and Marcelis, 1989). However, these authors showed that, when plotted against truss development stage, PGR was little affected by temperature. 
        # Therefore one set of parameter values is sufficient to describe the potential dry weight growth of trusses at different temperatures satisfactorily. (Heuvelink, 1996, Annals of Botany)
        r.MPGRFR = [list(map(lambda x: p.PD * p.POFA * p.POFB * (1 + exp(-p.POFB*(x - p.POFC)))^(1/(1-p.POFD)) / ((p.POFD-1) * (exp(p.POFB * (x - p.POFC)) + 1)), row)) for row in k.DVSF] # p.PD: plant density
        r.MPGRFR = [[a * b for a, b in zip(*rows)] for rows in zip(r.MPGRFR, LOH)] # Set MPGRFR of harvested leaves at 0.
        # Potential growth rate of fruits (PGRFR) is MPGRFR * CAF.
        # The cumulative adaptation factor (CAF) is a state variable calculated in wofost.py
        r.PGRFR = [list(map(lambda x: k.CAF * x, row)) for row in r.MPGRFR]

        # Structural DMC (sDMC)
        r.SDMC = p.SDMC

    @prepare_rates
    def calc_rates(self, day, drv):
        r  = self.rates
        p = self.params
        k = self.kiosk

        r.GRFR = [list(map(lambda x: k.DMI * x / k.TPGR, row)) for row in k.PGRFR] # List of dry mass partitioned to each fruit depending on its potential growth rate (PGRFR) 
        r.GRFRF = [list(map(lambda x: x / r.SDMC, row)) for row in r.GRFR] # Convert dry mass increase to fresh mass increase

    @prepare_states
    def integrate(self, day, delt=1.0):
        params = self.params
        r = self.rates
        s = self.states
        k = self.kiosk

        # Update fruit dry mass
        s.FD = list(map(lambda l1, l2: [sum(x) for x in zip(l1, l2)], s.FD, r.GRFR)) 
        # Update fruit fresh mass
        s.FF = list(map(lambda l1, l2: [sum(x) for x in zip(l1, l2)], s.FF, r.GRFRF)) 
        # Update fruit dry matter content
        s.DMC = [[a / b for a, b in zip(*rows)] for rows in zip(s.FD, s.FF)]

        # Update yield (dead fruit) and total fruit mass on plants (living fruit)
        s.WSO = 0.
        s.DWSO = 0.
        s.YWSO = 0.
        for i in range(0, len(s.FD)):
            for j in range(0, len(s.FD[i])):
                if s.DOHF[i][j] != None: # Harvested = Dead
                    s.DWSO += s.FD[i][j] # Cumulative yield (dry mass)
                    s.YWSO += s.FF[i][j] # Cumulative yield (fresh mass)
                else: # Not harvested yet = living
                    s.WSO += s.FD[i][j] # Total dry mass of fruits on plants
        s.TWSO = s.WSO + s.DWSO # Total dry mass of fruits (both living and dead)

        # Harvest scheme for updating DOHF
        # DOHF ... If the development stage (DVSF) of the fruit becomes over 1.0, then the fruit will be harvested.
        for i in range(0, len(s.DOHF)):
            for j in range(0, len(s.DOHF[i])):
                if s.DOHF[i][j] == None and k.DVSF[i][0] >= 1.0:
                    s.DOHF[i][j] = day
