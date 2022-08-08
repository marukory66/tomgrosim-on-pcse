# -*- coding: utf-8 -*-
#%%
# Naomichi Fujiuchi (naofujiuchi@gmail.com), April 2022
# This is a derivative work by Fujiuchi (GNU GPL license) from the original work PCSE by Allard de Wit (allard.dewit@wur.nl) (EUPL license).
# import datetime
from datetime import date
from datetime import timedelta
import math

from pcse.traitlets import Float, Int, Instance, Enum, Bool
from pcse.decorators import prepare_rates, prepare_states

from pcse.util import limit, daylength, AfgenTrait
from pcse.base import ParamTemplate, StatesTemplate, RatesTemplate, \
     SimulationObject, VariableKiosk
from pcse import signals
from pcse import exceptions as exc
import copy
import os
from pcse.fileinput import ExcelWeatherDataProvider,PCSEFileReader,CABOWeatherDataProvider
import pandas as np

#.xlsxファイルから情報を読み込むため
weatherfile = os.path.join("C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse/nl1.xlsx")
wdp = ExcelWeatherDataProvider(weatherfile) # daily weather observation

#%%
class DVS_Phenology(SimulationObject):

    # def __init__(self):
    #     pass

    class Parameters(ParamTemplate):
        # print("eeeeee")
        DVSI = Float(-99.)  # Initial development stage of plant (number of flowered truss)
        DVSFI   = Instance(list)  # Initial development stage of fruits
        DOELI = Instance(list)  # Initial data of day of emergence of leaves
        DOEFI = Instance(list)  # Initial data of day of emergence of fruits (day of anthesis)
        # DOHFI = Instance(list)  # Initial data of day of harvest of fruits
        CROP_START_TYPE = Enum(["sowing", "emergence"])
        CROP_END_TYPE = Enum(["maturity", "harvest", "earliest"])

    class RateVariables(RatesTemplate):
        pass

    class StateVariables(StatesTemplate):
        # print("ddddd")
        DVS = Float(-99.)  # Development stage of plant (number of flowered truss)
        DVSF = Instance(list)  # Development stage of fruits (0<=DVSF<=1)
        DOEL = Instance(list) # Day of emergence of leaves
        DOEF = Instance(list) # Day of emergence of fruits (Day of anthesis)
        DVR     = Float(-99.)  # development rate of a plant
        DVRF    = Instance(list)  # development rate of fruits
        
        # DOHF = Instance(list) # Day of harvest of fruits

    # def initialize(self, day, kiosk, parvalues):
    def initialize(self, day, kiosk):

        print("phenology.py")
        # self.params = self.Parameters(parvalues)
        self.kiosk = kiosk

        self._connect_signal(self._on_CROP_FINISH, signal=signals.crop_finish)

        lists = [[1 for i in range(4)] for j in range(5)]
        # list_DVSF = list()
        # list_DOEL = list()
        # list_DOEF = list()
        # list_DOHL = list()
        # list_DOHF = list()
        list_DVSF = copy.deepcopy(lists)
        # list_DOEL = copy.deepcopy(lists)
        # list_DOEF = copy.deepcopy(lists)
        list_DOHL = copy.deepcopy(lists)

        # list_DOHF = copy.deepcopy(lists)

        list_DVSF[0][0] = 1
        """
        葉の一果房目の左端と果実の4果房目の左側端が同じ日付になるlistを作成

        """
        # list_DOEF = copy.deepcopy(lists)
        # list_DOEF = [[0 for i in range(3)] for j in range(5)]

        # for index in range(15):
        #     for i in range(4):
        #         for ii in range(2):
        #             # print(index)
        #             list_DOEF[i][ii] = "{0:%Y/%m/%d}".format(date(2007,7,index+5))
      
        list_DOEF = []
        i = 0
        for a,index in enumerate(range(15)):
            listA = []
            while i <= 3:
                # listA.append("{0:%Y/%m/%d}".format(date(2007,7,index+5)))
                listA.append("{0:%Y/%m/%d}".format(date(2007,7,5+a)))

                list_DOEF.append(listA)
                i += 1
        print(list_DOEF)



        # for index in range(15):
        #     list_DOEF = "{0:%Y/%m/%d}".format(date(2007,7,index+5))

        # list_DOEF = None
        # for index in range(15):
        #     i_index= index//3
        #     ii_index = index % 4
        #     list_DOEF[i_index][ii_index] = "{0:%Y/%m/%d}".format(date(2007,7,index+5))


        list_DOHL[0][0] = lists
        # list_DOHF[0][0] = lists

        DVS =  1
        DVSF = list_DVSF
        # DOEL = list_DOEL
        DOEF = copy.deepcopy(list_DOEF)
        DVRF = copy.deepcopy(lists)
        DVR = 1
        # DOEL =  [[1 for i in range(3)] for j in range(5)]
        DOEL = copy.deepcopy(list_DOEF)  
        print("F_DOEF",DOEF)  


        # self.states = self.StateVariables(kiosk, publish=["DVS","DVSF","DOEL","DOHF"],
        #                                   DVS=DVS, DVSF=DVSF,
        #                                   DOEL=DOEL, DOEF=DOEF,
        #                                   DOHF=DOHF)



        # self.states = self.StateVariables(kiosk, publish=["DVS","DVSF","DOEL","DOEF","DVRF","DVR"],
        #                                   DVS=DVS, DVSF=DVSF,DVRF=DVRF,DVR=DVR,
        #                                   DOEL=DOEL, DOEF=DOEF
        #                                   )
        
        
        # self.states = self.StateVariables(kiosk)
        
        self.states = self.StateVariables(kiosk, publish=["DVS","DVSF","DOEL","DOEF","DVRF","DVR"],
                                          DVS=DVS, DVSF=DVSF,DVRF=DVRF,DVR=DVR,
                                          DOEL=DOEL, DOEF=DOEF
                                          )
        
        
        self.rates = self.RateVariables(kiosk)
        
        print("kiosk",kiosk)

    @prepare_rates
    def calc_rates(self, day, drv):

        p = self.params 
        r = self.rates
        s = self.states
        k = self.kiosk
        # kiosk = self.kiosk 

        # print(day)
        # print(type(day))
        # print(type(date(day)))
        # print(type(date(2007,7,3)))
        # drv = wdp(date(day))
        drv = wdp(day)

        # drv = wdp(date(2007,7,3))
         
        drvTEMP = ((drv.TMIN + drv.TMAX)/2)

        # drvTEMP = self.drvtemp


        # Development rate of a plant (DVR) depends on daily mean temperature (drv.TEMP) and plant age (DVS).
        # r.DVR = self._dev_rate_plant(drv.TEMP, s.DVS)
        # DVSを1で動かしています

        #r.DVR = self._dev_rate_plant(16,1)


        r.DVR = self._dev_rate_plant(drvTEMP,s.DVS)


        # Development rate of a fruit (DVRF) depends on temperature and the developmet stage of the fruit.
        # The function to calculate DVRF is applied to each element of s.DVSF

        
        # r.DVRF = [list(map(lambda x: self._dev_rate_fruit(drv.TEMP, x), row)) for row in s.DVSF]
        # r.DVRF = [list(map(self._dev_rate_fruit(drvTEMP, row) for row in s.DVSF))]
        
        # drvTEMP_list = copy.deepcopy(s.DVSF)
        # drvTEMP_list[:] = [drvTEMP]
        # drvTEMP_list 　map関数を使用するために，s.DVSF分のdrvTEMPを作成
        # drvTEMP_list = copy.deepcopy(s.DVSF)
        drvTEMP_list = [[1 for i in range(4)] for j in range(5)]

        drvTEMP_list = [drvTEMP for i ,w in enumerate(drvTEMP_list)]
        drvTEMP_list = [int(i) for i in drvTEMP_list]
        # print(drvTEMP_list)
        # print(type(drvTEMP_list[0]))
        # print(s.DVSF)
        # r.DVRF =  [list(map(self._dev_rate_fruit , drvTEMP_list ,s.DVSF))]
        DVRF =  [list(map(lambda x: self._dev_rate_fruit(drvTEMP, x), row)) for row in k.DVSF]
        # r.DVRF =  [list(map(lambda x: self._dev_rate_fruit(drvTEMP, x), row) for row in s.DVSF)]
        
        


        # aaaa =  [list(map(self._dev_rate_fruit , [2,3,4,6,7] ,[2,3,4,6,7]))]
        # r.DVRF =  [list(map(self._dev_rate_fruit , drvTEMP_list ,[2,3,4,6,7]))]
        # msg = "Finished rate calculation for %s"
        # self.logger.debug(msg % day)
        # self.rates = self.RateVariables(kiosk, publish=["DVR","DVRF"],DVR=None, DVRF=None)

    def _dev_rate_plant(self, drvTEMP, sDVS):
        # Development rate of a plant (DVR) depends on daily mean temperature (drv.TEMP) and plant age (DVS).
        # DVR was called as "Flowering rate (FR)" in De Koning (1994, Ph.D. thesis), and the equation of FR was as follows (p.42 [eqn 3.2.3] in De Koning (1994, Ph.D. thesis)):
        # FR[t] = a + 0.1454 * ln(T[t]) - 0.001 * A[t-1]
        # A[t] = A[t-1] + FR[t]
        # where a is a cultivar dependent parameter, T is 24-h mean temperature (17-27 C), and A is the plant's physiological age expressed as the number of the flowering truss.
        # a = -0.296 ('Calypso'), -0.286 ('Counter'), -0.276 ('Liberto'), -0.302 ('Dimbito')
        # Here, the value of teh parameter 'a' is set at -0.286 ('Counter').
        rDVR = -0.286 + 0.1454 * math.log(drvTEMP) - 0.001 * sDVS
        return(rDVR)

    def _dev_rate_fruit(self,drvTEMP, sDVSF):
        # Development rate of a fruit (DVRF) depends on temperature and the developmet stage of the fruit.
        # De Koning (1994, Ph.D. thesis) (and Heuvelink (1996, Annals of Botany)) used the following equation for DVRF. It described fruit growth period in cv. Counter quite well (unpublished research, Heuvelink, 1996).
        if(sDVSF == None): 
            rDVRF = None
        else:
            rDVRF = 0.0181 + math.log(drvTEMP/20) * (0.0392 - 0.213 * sDVSF + 0.415 * sDVSF**2 - 0.24 * sDVSF**3)
        return(rDVRF)

    @prepare_states
    def integrate(self,day, delt=1.0):

        p = self.params
        r = self.rates
        s = self.states
        k = self.kiosk
        print("integrate",k)
        # Integrate phenologic states
        # s.DVS += k.DVR
        
        #回しすぎると超える？
        s.DVS = 1
        
        
        # s.DVS += r.DVR
        # s.DVSF = list(map(lambda l1, l2: [sum(x) for x in zip(l1, l2)], s.DVSF, r.DVRF))
        # print("AAA",k.DVSF)
        # print("AAAA",r.DVRF)
        #DVRFがintegrateだけで動かす時に，使用できないために仮置き
        # r.DVRF = [[1 for i in range(4)] for j in range(5)]

        # s.DVSF = list(map(lambda l1, l2: [sum(x) for x in zip(l1, l2)], s.DVSF, r.DVRF))
        
        k.DVSF = list(map(lambda l1, l2: [sum(x) for x in zip(l1, l2)], k.DVSF, k.DVRF))
        
        # print(s.DVSF)
        # 1) Add the flower anthesis after the 2nd flower
        # If 1st flower already anthesis, then add the anthesis date of following flowers.
        # If 1st flower not anthesis yet, then the following anthesis will not be added.
        # The interval between anthesis of a flower and a next flower was set at 1 d.
        # 2) Check if 1st flower anthesis of a truss and the 1st leaf emergence are reached
        # A vegetative unit (stem and three leaves between two trusses) starts to grow
        # about 3 weeks (depending on temperature) before the corresponding truss,
        # e.g. at anthesis of truss 5, vegetative unit 8 starts to grow. (Heuvelink, 1996, Annals of Botany)
        # Here, when a 1st flower of a truss anthesis, the 1st leaf of the 3-trusses-above turss emerges.
        # 3) Add the leaf emergence after the 2nd leaf
        #
        for i in range(0, int(s.DVS)):
            # 1)
            if s.DOEF[i][0] != None:
                for j in range(1, len(s.DOEF[i])):
                    if s.DOEF[i][j] != None:
                        continue
                    else:
                        s.DOEF[i][j] = day
                        break
            # 2)
            else:
                s.DOEF[i][0] = day
                if s.DOEL[i+3][0] == None:
                    s.DOEL[i+3][0] = day
        # 3)
        if s.DVS % 1 >= 2/3:
            nLEAF = 3
        elif s.DVS % 1 >= 1/3:
            nLEAF = 2
        else:
            nLEAF = 1
        # for i in range(0, int(s.DVS+2)):
        print("DVS",s.DVS)
        for i in range(0, int(s.DVS+1)):
            for j in range(0,3):
                if s.DOEL[i][j] == None:
                    s.DOEL[i][j] = day
        print(s.DOEL)
        # print("DVS",s.DVS)
        i = int(s.DVS)
        # i = s.DVS + 3
        if s.DOEL[i][0] == None:
            s.DOEL[i][0] = day
        if s.DOEL[i][1] == None and nLEAF >= 2:
            s.DOEL[i][1] = day
        if s.DOEL[i][2] == None and nLEAF == 3:
            s.DOEL[i][0] = day

        msg = "Finished state integration for %s"
        self.logger.debug(msg % day)

    def _on_CROP_FINISH(self, day, finish_type=None):
        """Handler for setting day of harvest (DOH). Although DOH is not
        strictly related to phenology (but to management) this is the most
        logical place to put it.
        """
        if finish_type in ['harvest', 'earliest']:
            self._for_finalize["DOH"] = day

# %%
