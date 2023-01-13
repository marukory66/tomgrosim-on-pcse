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
        # SPA  = Float(-99.)
        # TDWI = Float(-99.)
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



    def initialize(self, day, kiosk, parvalues):

        self.params = self.Parameters(parvalues)
        self.kiosk = kiosk
        # INITIAL STATES
        params = self.params

        FD = params.FDI # List of dry mass of fruits. Weights of the fruits that have not generated yet are 0.
        DMC = params.DMCI # List of dry matter content (DMC). DMCs of the leaves that have not generated yet are None.
        FF = params.FFI # List of fresh mass of fruits. Weights of the fruits that have not generated yet are 0.
        DOHF = params.DOHFI
        DOHF = [list(map(lambda x: None if x == 'None' else x, row)) for row in DOHF]
        FF = [list(map(lambda x: None if x == 'None' else x, row)) for row in FF]
        DMC = [list(map(lambda x: None if x == 'None' else x, row)) for row in DMC]
        FD = [list(map(lambda x: None if x == 'None' else x, row)) for row in FD]


        WSO = 0.
        DWSO = 0.
        YWSO = 0.
        for i in range(0, len(FD)):
            # for j in range(0, len(FD[i])):
            for j in range(0, len(FD[i])):
                if DOHF[i][j] != None: # Harvested = Dead
                # if DOHF[i][j] != str(None): # Harvested = Dead
                    DWSO += float(FD[i][j]) # Cumulative yield (dry mass)
                    YWSO += float(FF[i][j]) # Cumulative yield (fresh mass)
                else: # Not harvested yet = living
                    if FD[i][j] != None:
                        WSO += float(FD[i][j])
                    else:
                        pass
        
        TWSO = WSO + DWSO # Total dry mass of fruits (both living and dead)
        self.states = self.StateVariables(kiosk, publish=["FD","DMC","FF","DOHF","WSO","DWSO","YWSO","TWSO","GRFR","PGRFR","MPGRFR","SDMC","FRAGE"],
                                          FD=FD, DMC=DMC, FF=FF, DOHF=DOHF,GRFR=[], GRFRF=[], PGRFR=[], MPGRFR=[], SDMC=None, FRAGE=[],
                                          WSO=WSO, DWSO=DWSO, YWSO=YWSO, TWSO=TWSO)
        self.rates = self.RateVariables(kiosk)
    @prepare_rates
    def calc_potential(self,  day, drv):

        
        k = self.kiosk
        r = self.rates
        p = self.params

        # List of harvested (0: harvested, 1: not yet harvested)
        # LOH = k.DOHF

        LOH = copy.deepcopy(k.DOHF)
        for i in range(0, len(k.DOHF)):
            for j in range(0, len(k.DOHF[i])):
                if k.DOHF[i][j] == None:
                    LOH[i][j] = 1
                else:
                    LOH[i][j] = 0
        # k.FRAGE = k.DOEF
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
        
        # k.MPGRFR = [list(map(lambda x: p.PD * p.POFA * p.POFB * (1 + exp(-p.POFB*(x - p.POFC)))**(1/(1-p.POFD)) / ((p.POFD-1) * (exp(p.POFB * (x - p.POFC)) + 1)), row )) for row in k.DVSF] # p.PD: plant density
        def MPGRFR_(x,y,z):
            if x != None and y != None and z != None:
                return x*y*z
            else:
                pass
        
        
        k.MPGRFR = [list(map(lambda x: p.PD * p.POFA * p.POFB * (1 + exp(-p.POFB*(x - p.POFC)))**(1/(1-p.POFD)) / ((p.POFD-1) * (exp(p.POFB * (x - p.POFC)) + 1)) if isinstance(x,float) else None, row )) for row in k.DVSF] # p.PD: plant density
        # k.MPGRFR = [[a * b for a, b in zip(*rows)] for rows in zip(k.MPGRFR, LOH)] # Set MPGRFR of harvested fruits at 0.
        # k.MPGRFR = [[MPGRFR_(a,b) for a, b in zip(*rows)] for rows in zip(k.MPGRFR, LOH)] 
        k.MPGRFR = [[MPGRFR_(a,b,c) for a, b, c in zip(*rows)] for rows in zip(k.MPGRFR, LOH,k.DVRF)]
        # # Potential growth rate of fruits (PGRFR) is MPGRFR * CAF.
        # The cumulative adaptation factor (CAF) is a state variable calculated in wofost.py
        # k.PGRFR = [list(map(lambda x: k.CAF * x, row)) for row in k.MPGRFR]
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
        # k.GRFR = [list(map(lambda x: k.DMI * x / k.TPGR, row)) for row in k.PGRFR] # List of dry mass partitioned to each fruit depending on its potential growth rate (PGRFR)
        # k.GRFRF = [list(map(lambda x: x / k.SDMC, row)) for row in k.GRFR] # Convert dry mass increase to fresh mass increase


    @prepare_states
    def integrate(self,day, delt=1.0):
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
        # k.FD = list(map(lambda l1, l2: [sum(x) for x in zip(l1, l2)], k.FD, k.GRFR))
        k.FD = list(map(lambda l1, l2: [sum_(x) for x in zip(l1, l2)], k.FD, k.GRFR))
        # Update fruit fresh mass
        # k.FF = list(map(lambda l1, l2: [sum(x) for x in zip(l1, l2)], k.FF, k.GRFRF))
        k.FF = list(map(lambda l1, l2: [sum_(x) for x in zip(l1, l2)], k.FF, k.GRFRF))
        # print("k.FD",k.FD)

        # Update fruit dry matter content
        # k.DMC = [[a / b for a, b in zip(*rows)] for rows in zip(k.FD, k.FF)]

        
        k.DMC = [[None if a==None or b==None or a==0 or b==0 else a / b for a, b in zip(*rows) ] for rows in zip(k.FD, k.FF)]
        
        
        # Update yield (dead fruit) and total fruit mass on plants (living fruit)
        k.WSO = 0.
        k.DWSO = 0.
        k.YWSO = 0.
        print("k.YWSO_reset",k.YWSO)
        # for i in range(0, len(k.FD)):
        #     for j in range(0, len(k.FD[i])):YWSO
        #         if k.DOHF[i][j] != None: # Harvested = Dead
        #             k.DWSO += k.FD[i][j] # Cumulative yield (dry mass)
        #             k.YWSO += k.FF[i][j] # Cumulative yield (fresh mass)
        #         else: # Not harvested yet = living
        #             k.WSO += k.FD[i][j] # Total dry mass of fruits on plants
        # k.TWSO = k.WSO + k.DWSO # Total dry mass of fruits (both living and dead)

        for i in range(0, len(k.FD)):
            for j in range(0, len(k.FD[i])):
                if k.DOHF[i][j] != None: # Harvested = Dead
                    k.DWSO += k.FD[i][j] # Cumulative yield (dry mass)
                    k.YWSO += k.FF[i][j] # Cumulative yield (fresh mass)
                else: # Not harvested yet = living
                    if type(k.FD[i][j]) == int() or float():
                        k.WSO += k.FD[i][j] # Total dry mass of fruits on plants
        k.TWSO = k.WSO + k.DWSO # Total dry mass of fruits (both living and dead)
        print("k.YWSO",k.YWSO)
        # for i in range(0, len(k.FD)):
        #     for j in range(0, len(k.FD[i])):
        #         if k.DOHF[i][j] != None: # Harvested = Dead
        #             if  k.FF[i][j] != "F":
        #                 k.DWSO += k.FD[i][j] # Cumulative yield (dry mass)
        #                 k.YWSO += k.FF[i][j] # Cumulative yield (fresh mass)
        #                 k.FF[i][j] = "F"
        #         else: # Not harvested yet = living
        #             if type(k.FD[i][j]) == int() or float():
        #                 k.WSO += k.FD[i][j] # Total dry mass of fruits on plants
        # k.TWSO = k.WSO + k.DWSO # Total dry mass of fruits (both living and dead)
        

        # Harvest scheme for updating DOHF
        # DOHF ... If the development stage (DVSF) of the fruit becomes over 1.0, then the fruit will be harvested.
        # for i in range(0, len(k.DOHF)):
        #     for j in range(0, len(k.DOHF[i])):
        #         if k.DOHF[i][j] == None and k.DVSF[i][j] >= 1.0:
        #             k.DOHF[i][j] = day
        for i in range(0, len(k.DOHF)):
            for j in range(0, len(k.DOHF[i])):
                if k.DVSF[i][j] == None :
                    pass
                elif k.DOHF[i][j] == None and k.DVSF[i][j] >= 1.0:
                    k.DOHF[i][j] = day
                else:
                    pass
        
        #初期値を与えたlist

        csv_FF = "C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse/test/k.FF.csv"        
        
        with open(csv_FF, mode="a", encoding="utf-8") as f:
            f.write(str(day)+",")
            writer = csv.writer(f, lineterminator='\n')
            writer.writerows([k.FF])
        
        csv_FD = "C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse/test/k.FD.csv"        
        
        with open(csv_FD, mode="a", encoding="utf-8") as f:
            f.write(str(day)+",")
            writer = csv.writer(f, lineterminator='\n')
            writer.writerows([k.FD])

        csv_DVSF = "C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse/test/k.DVSF.csv"        
        
        with open(csv_DVSF, mode="a", encoding="utf-8") as f:
            f.write(str(day)+",")
            writer = csv.writer(f, lineterminator='\n')
            writer.writerows([k.DVSF])
        
        csv_LV = "C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse/test/k.LV.csv"        
        
        with open(csv_LV, mode="a", encoding="utf-8") as f:
            f.write(str(day)+",")
            writer = csv.writer(f, lineterminator='\n')
            writer.writerows([k.LV])
        
        csv_DOHL = "C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse/test/k.DOHL.csv"        
        
        with open(csv_DOHL, mode="a", encoding="utf-8") as f:
            f.write(str(day)+",")
            writer = csv.writer(f, lineterminator='\n')
            writer.writerows([k.DOHL])
        
        csv_DOEL = "C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse/test/k.DOEL.csv"        
        
        with open(csv_DOEL, mode="a", encoding="utf-8") as f:
            f.write(str(day)+",")
            writer = csv.writer(f, lineterminator='\n')
            writer.writerows([k.DOEL])

        csv_GRFR = "C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse/test/k.GRFR.csv"        
        
        with open(csv_GRFR, mode="a", encoding="utf-8") as f:
            f.write(str(day)+",")
            writer = csv.writer(f, lineterminator='\n')
            writer.writerows([k.GRFR])

        csv_GRFRF = "C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse/test/k.GRFRF.csv"        
        
        with open(csv_GRFRF, mode="a", encoding="utf-8") as f:
            f.write(str(day)+",")
            writer = csv.writer(f, lineterminator='\n')
            writer.writerows([k.GRFRF])

        csv_PGRFR = "C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse/test/k.PGRFR.csv"        
        
        with open(csv_PGRFR, mode="a", encoding="utf-8") as f:
            f.write(str(day)+",")
            writer = csv.writer(f, lineterminator='\n')
            writer.writerows([k.PGRFR])

        csv_MPGRFR = "C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse/test/k.MPGRFR.csv"        
        
        with open(csv_MPGRFR, mode="a", encoding="utf-8") as f:
            f.write(str(day)+",")
            writer = csv.writer(f, lineterminator='\n')
            writer.writerows([k.MPGRFR])

        csv_FRAGE = "C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse/test/k.FRAGE.csv"        
        
        with open(csv_FRAGE, mode="a", encoding="utf-8") as f:
            f.write(str(day)+",")
            writer = csv.writer(f, lineterminator='\n')
            writer.writerows([k.FRAGE])

        csv_DMC = "C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse/test/k.DMC.csv"        
        
        with open(csv_DMC, mode="a", encoding="utf-8") as f:
            f.write(str(day)+",")
            writer = csv.writer(f, lineterminator='\n')
            writer.writerows([k.DMC])
        
        csv_DOEF = "C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse/test/k.DOEF.csv"        
        
        with open(csv_DOEF, mode="a", encoding="utf-8") as f:
            f.write(str(day)+",")
            writer = csv.writer(f, lineterminator='\n')
            writer.writerows([k.DOEF])
        
        csv_DOHF = "C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse/test/k.DOHF.csv"        
        
        with open(csv_DOHF, mode="a", encoding="utf-8") as f:
            f.write(str(day)+",")
            writer = csv.writer(f, lineterminator='\n')
            writer.writerows([k.DOHF])
        
        csv_LA = "C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse/test/k.LA.csv"        
        
        with open(csv_LA, mode="a", encoding="utf-8") as f:
            f.write(str(day)+",")
            writer = csv.writer(f, lineterminator='\n')
            writer.writerows([k.LA])
        
        csv_SLA = "C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse/test/k.SLA.csv"        
        
        with open(csv_SLA, mode="a", encoding="utf-8") as f:
            f.write(str(day)+",")
            writer = csv.writer(f, lineterminator='\n')
            writer.writerows([k.SLA])

        #初期値を与えず計算するlist
        
        csv_ACL = "C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse/test/k.ACL.csv"        
        
        with open(csv_ACL, mode="a", encoding="utf-8") as f:
            f.write(str(day)+",")
            writer = csv.writer(f, lineterminator='\n')
            writer.writerows([k.ACL])

        csv_GRLV = "C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse/test/k.GRLV.csv"        
        
        with open(csv_GRLV, mode="a", encoding="utf-8") as f:
            f.write(str(day)+",")
            writer = csv.writer(f, lineterminator='\n')
            writer.writerows([k.GRLV])

        csv_POL = "C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse/test/k.POL.csv"        
        
        with open(csv_POL, mode="a", encoding="utf-8") as f:
            f.write(str(day)+",")
            writer = csv.writer(f, lineterminator='\n')
            writer.writerows([k.POL])
        
        csv_LVAGE = "C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse/test/k.LVAGE.csv"        
        
        with open(csv_LVAGE, mode="a", encoding="utf-8") as f:
            f.write(str(day)+",")
            writer = csv.writer(f, lineterminator='\n')
            writer.writerows([k.LVAGE])

        csv_PGRLV = "C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse/test/k.PGRLV.csv"        
        
        with open(csv_PGRLV, mode="a", encoding="utf-8") as f:
            f.write(str(day)+",")
            writer = csv.writer(f, lineterminator='\n')
            writer.writerows([k.PGRLV])
        
        csv_MPGRLV = "C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse/test/k.MPGRLV.csv"        
        
        with open(csv_MPGRLV, mode="a", encoding="utf-8") as f:
            f.write(str(day)+",")
            writer = csv.writer(f, lineterminator='\n')
            writer.writerows([k.MPGRLV])

        csv_DVRF = "C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse/test/k.DVRF.csv"        
        
        with open(csv_DVRF, mode="a", encoding="utf-8") as f:
            f.write(str(day)+",")
            writer = csv.writer(f, lineterminator='\n')
            writer.writerows([k.DVRF])
        
        csv_RGRL = "C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse/test/k.RGRL.csv"        

        with open(csv_RGRL, mode="a", encoding="utf-8") as f:
            f.write(str(day)+",")
            writer = csv.writer(f, lineterminator='\n')
            writer.writerows([k.RGRL])
        
        csv_ASSIM = "C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse/test/k.ASSIM.csv"        

        with open(csv_ASSIM, mode="a", encoding="utf-8") as f:
            f.write(str(day)+",")
            writer = csv.writer(f, lineterminator='\n')
            writer.writerows([k.ASSIM])

        #各日にちごとの葉の枚数を算出
        output_LV = copy.deepcopy(k.LV)
        for i in range(0, len(k.LV)):
            for j in range(0, len(k.LV[i])):
                if k.LV[i][j] != None:
                    if k.DOHL[i][j] == None:
                        output_LV[i][j] = 1
                    else:
                        output_LV[i][j] = 0    
                else:
                    output_LV[i][j] = 0
        
        csv_LOH = "C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse/test/k.LOH.csv"        
        with open(csv_LOH, mode="a", encoding="utf-8") as f:
            f.write(str(day)+",")
            writer = csv.writer(f, lineterminator='\n')
            writer.writerow([sum(map(sum, output_LV))])    


        data_list = []
        if str(day) == "2006-04-01":
            data_list.append(["param","WSO","DWSO","YWSO","TWSO","SDMC","TDM","GASST","MREST","ASA","AF","CAF","DMI","CVF","DMA","GASS","MRES","ASRC","WRO","TWRO","GRRO","TWST","WST","GRST","LAI","WLV","DWLV","SSLA","FR","FL","FS","FO","TPGR","TMPGR","TPGRLV","TMPGRLV","TPGRFR","TMPGRFR","TPGRST","TPGRRO","PF","DVS","DVR","RGR"])
        data_list.append([day,k.WSO,k.DWSO,k.YWSO,k.TWSO,k.SDMC,k.TDM,k.GASST,k.MREST,k.ASA,k.AF,k.CAF,k.DMI,k.CVF,k.DMA,k.GASS,k.MRES,k.ASRC,k.WRO,k.TWRO,k.GRRO,k.TWST,k.WST,k.GRST,k.LAI,k.WLV,k.DWLV,k.SSLA,k.FR,k.FL,k.FS,k.FO,k.TPGR,k.TMPGR,k.TPGRLV,k.TMPGRLV,k.TPGRFR,k.TMPGRFR,k.TPGRST,k.TPGRRO,k.PF,k.DVS,k.DVR,k.RGR])
        df = pd.DataFrame(data_list)
 
        #CSVに出力
        df.to_csv("C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse/test/f_param.csv",mode="a",index=False,header=False)


# %%
