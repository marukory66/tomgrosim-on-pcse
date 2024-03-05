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
import copy
from datetime import datetime as dt
from functools import reduce
import csv
import numpy as np
import pandas as pd
#%%
class TOMGROSIM_Storage_Organ_Dynamics(SimulationObject):

    class Parameters(ParamTemplate):
        FDI = Instance(list)
        DMCI = Instance(list)
        FFI = Instance(list)
        DOHFI = Instance(list)
        PD  = Float(-99.)
        POFA = Float(-99.)
        POFB = Float(-99.)
        POFC = Float(-99.)
        POFD = Float(-99.)
        SDMC = Float(-99.)

    class RateVariables(RatesTemplate):
        pass

    class StateVariables(StatesTemplate):
        FD = Instance(list)
        DMC = Instance(list)
        FF = Instance(list)
        DOHF = Instance(list)
        WSO  = Float(-99.) # Weight living storage organs
        DWSO = Float(-99.) # Weight dead storage organs (Cumulative yield (dry mass))
        YWSO = Float(-99.) # Cumulative yield (fresh mass)
        TWSO = Float(-99.) # Total weight storage organs (Dry mass)
        GRFR = Instance(list) # Actual growth rate of a fruit
        GRFRF = Instance(list) # Actual growth rate of a fruit on a fresh mass basis
        PGRFR = Instance(list) # Potential growth rate of a fruit
        MPGRFR = Instance(list) # Maximum potential growth rate of a fruit
        SDMC = Float(-99.) # Structural dry matter content of a fruit
        FRAGE = Instance(list) # Age of a fruit [d]
        NOHF = Float(-99.) # number of harbest fruit

    def initialize(self, day, kiosk, parvalues,cropinitiallist):

        self.params = self.Parameters(parvalues)
        self.kiosk = kiosk
        # INITIAL STATES
        params = self.params

        FD = cropinitiallist["FDI"] # List of dry mass of fruits. Weights of the fruits that have not generated yet are 0.
        DMC = cropinitiallist["DMCI"] # List of dry matter content (DMC). DMCs of the leaves that have not generated yet are None.
        FF = cropinitiallist["FFI"] # List of fresh mass of fruits. Weights of the fruits that have not generated yet are 0.
        DOHF = cropinitiallist["DOHFI"]

        DOHF = [list(map(lambda x: x if x != "None"  else None, row)) for row in DOHF]
        FF = [list(map(lambda x: float(x) if x != "None"  else None, row)) for row in FF]
        DMC = [list(map(lambda x: float(x) if x != "None"  else None, row)) for row in DMC]
        FD = [list(map(lambda x: float(x) if x != "None"  else None, row)) for row in FD]
        WSO = 0.
        DWSO = 0.
        YWSO = 0.
        for i in range(0, len(FD)):
            for j in range(0, len(FD[i])):
                if DOHF[i][j] != None: # Harvested = Dead
                    DWSO += float(FD[i][j]) # Cumulative yield (dry mass)
                    YWSO += float(FF[i][j]) # Cumulative yield (fresh mass)
                else: # Not harvested yet = living
                    if FD[i][j] != None:
                        WSO += float(FD[i][j])
                    else:
                        pass
        TWSO = WSO + DWSO # Total dry mass of fruits (both living and dead)
        NOHF = 0
        self.states = self.StateVariables(kiosk, publish=["NOHF","FD","DMC","FF","DOHF","WSO","DWSO","YWSO","TWSO","GRFR","PGRFR","MPGRFR","SDMC","FRAGE","NOHF"],
                                          NOHF=NOHF,FD=FD, DMC=DMC, FF=FF, DOHF=DOHF,GRFR=[], GRFRF=[], PGRFR=[], MPGRFR=[], SDMC=None, FRAGE=[],
                                          WSO=WSO, DWSO=DWSO, YWSO=YWSO, TWSO=TWSO)
        self.rates = self.RateVariables(kiosk)
    @prepare_rates
    def calc_potential(self,  day, drv):

        k = self.kiosk
        r = self.rates
        p = self.params
        LOH = copy.deepcopy(k.DOHF)
        for i in range(0, len(k.DOHF)):
            for j in range(0, len(k.DOHF[i])):
                if k.DOHF[i][j] == None:
                    LOH[i][j] = 1
                else:
                    LOH[i][j] = 0
        k.FRAGE = copy.deepcopy(k.DOEF)
        for i in range(0, len(k.DOEF)):
            for j in range(0, len(k.DOEF[i])):
                if k.DOEF[i][j] != None:
                    k.FRAGE[i][j] = k.DOEF[i][j]
                else:
                    k.FRAGE[i][j] = 0
        # List of potential fruit growth rate of each fruit
        # The potential growth rate of a truss (PGR) is given by the first derivative of the Richards growth function (Richards, 1959),
        # relating fruit dry weight to time after anthesis (Heuvelink and Marcelis, 1989). However, these authors showed that, when plotted against truss development stage, PGR was little affected by temperature.
        # Therefore one set of parameter values is sufficient to describe the potential dry weight growth of trusses at different temperatures satisfactorily. (Heuvelink, 1996, Annals of Botany)
        # r.MPGRFR = [list(map(lambda x: p.PD * p.POFA * p.POFB * (1 + exp(-p.POFB*(x - p.POFC)))**(1/(1-p.POFD)) / ((p.POFD-1) * (exp(p.POFB * (x - p.POFC)) + 1)), row)) for row in k.DVSF] # p.PD: plant density

        def MPGRFR_(x,y,z):
            if x != None and y != None and z != None:
                return x*y*z
            else:
                pass

        # k.MPGRFR = [list(map(lambda x: p.PD * p.POFA * p.POFB * (1 + exp(-p.POFB*(x - p.POFC)))**(1/(1-p.POFD)) / ((p.POFD-1) * (exp(p.POFB * (x - p.POFC)) + 1)) if isinstance(x,float) else None, row )) for row in k.DVSF]
        k.MPGRFR = [list(map(lambda x: p.PD * p.POFA * p.POFB * (1 + exp(-p.POFB*(x - p.POFC)))**(1/(1-p.POFD)) / ((p.POFD-1) * (exp(p.POFB * (x - p.POFC)) + 1)) if isinstance(x,float) and x < 100 else None, row )) for row in k.DVSF] # p.PD: plant density
        k.MPGRFR = [[MPGRFR_(a,b,c) for a, b, c in zip(*rows)] for rows in zip(k.MPGRFR, LOH,k.DVRF)]
        # The cumulative adaptation factor (CAF) is a state variable calculated in wofost.py
        k.PGRFR = [list(map(lambda x: k.CAF * x if isinstance(x,float) else None, row)) for row in k.MPGRFR]

    @prepare_rates
    def calc_rates(self, day, drv):
        r = self.rates
        p = self.params
        k = self.kiosk

        # Structural DMC (sDMC)
        k.SDMC = p.SDMC

        k.GRFR = [list(map(lambda x: k.DMI * x / k.TPGR if isinstance(x,float) else None, row)) for row in k.PGRFR] # List of dry mass partitioned to each fruit depending on its potential growth rate (PGRFR)
        k.GRFRF = [list(map(lambda x: x / k.SDMC if isinstance(x,float) else None, row)) for row in k.GRFR] # Convert dry mass increase to fresh mass increase

    @prepare_states
    def integrate(self,day,delt=1.0):
        params = self.params
        r = self.rates
        s = self.states
        k = self.kiosk

        def sum_(x):
            if x[0]==None and x[1]==None:
                pass
            elif x[0]!=None and x[1]==None:
                return x[0]
            else:
                return sum(x)
        # Update fruit dry mass
        k.FD = list(map(lambda l1, l2: [sum_(x) for x in zip(l1, l2)], k.FD, k.GRFR))

        # Update fruit fresh mass
        k.FF = list(map(lambda l1, l2: [sum_(x) for x in zip(l1, l2)], k.FF, k.GRFRF))

        # Update fruit dry matter content
        k.DMC = [[None if a==None or b==None or a==0 or b==0 else a / b for a, b in zip(*rows) ] for rows in zip(k.FD, k.FF)]

        # Update yield (dead fruit) and total fruit mass on plants (living fruit)
        k.WSO = 0.
        k.DWSO = 0.
        k.YWSO = 0.

        for i in range(0, len(k.FD)):
            for j in range(0, len(k.FD[i])):
                if k.DOHF[i][j] != None: # Harvested = Dead
                    k.DWSO += k.FD[i][j] # Cumulative yield (dry mass)
                    k.YWSO += k.FF[i][j] # Cumulative yield (fresh mass)
                else: # Not harvested yet = living
                    if k.FD[i][j] != None:
                        k.WSO += k.FD[i][j] # Total dry mass of fruits on plants
        k.TWSO = k.WSO + k.DWSO # Total dry mass of fruits (both living and dead)
        # Harvest scheme for updating DOHF
        # DOHF ... If the development stage (DVSF) of the fruit becomes over 1.0, then the fruit will be harvested.

        k.NOHF = 0

        for i in range(0, len(k.DOHF)):
            for j in range(0, len(k.DOHF[i])):
                if k.DVSF[i][j] == None :
                    pass
                elif k.DOHF[i][j] == None and k.DVSF[i][j] >= float(1.13885374273369+0.05):
                    k.DOHF[i][j] = day
                    k.NOHF += 1
                else:
                    pass
