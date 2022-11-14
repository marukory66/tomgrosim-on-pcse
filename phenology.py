# -*- coding: utf-8 -*-
#%%
# Naomichi Fujiuchi (naofujiuchi@gmail.com), April 2022
# This is a derivative work by Fujiuchi (GNU GPL license) from the original work PCSE by Allard de Wit (allard.dewit@wur.nl) (EUPL license).
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
# import test_sample
weatherfile = os.path.join("C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse/nl1.xlsx")
wdp = ExcelWeatherDataProvider(weatherfile) # daily weather observation
# wdp = test_sample.wdp
#%%
class DVS_Phenology(SimulationObject):
    class Parameters(ParamTemplate):
        DVSI = Float(-99.)  # Initial development stage of plant (number of flowered truss)
        DVSFI   = Instance(list)  # Initial development stage of fruits
        DOELI = Instance(list)  # Initial data of day of emergence of leaves
        DOEFI = Instance(list)  # Initial data of day of emergence of fruits (day of anthesis)
        CROP_START_TYPE = Enum(["sowing", "emergence"])
        CROP_END_TYPE = Enum(["maturity", "harvest", "earliest"])

    class RateVariables(RatesTemplate):
        pass

    class StateVariables(StatesTemplate):
        DVS = Float(-99.)  # Development stage of plant (number of flowered truss)
        DVSF = Instance(list)  # Development stage of fruits (0<=DVSF<=1)
        DOEL = Instance(list) # Day of emergence of leaves
        DOEF = Instance(list) # Day of emergence of fruits (Day of anthesis)
        DVR     = Float(-99.)  # development rate of a plant
        DVRF    = Instance(list)  # development rate of fruits

    def initialize(self, day, kiosk, parvalues):
        self.kiosk = kiosk
        self._connect_signal(self._on_CROP_FINISH, signal=signals.crop_finish)

        self.params = self.Parameters(parvalues)
        # print(self.params)
        DVS = self.params.DVSI
        DVSF = self.params.DVSFI
        DOEL = self.params.DOELI
        DOEF = self.params.DOEFI

        self.states = self.StateVariables(kiosk, publish=["DVS","DVSF","DOEL","DOEF","DVRF","DVR"],
                                          DVS=DVS, DVSF=DVSF,DVRF=[],DVR=None,
                                          DOEL=DOEL, DOEF=DOEF
                                          )
        self.rates = self.RateVariables(kiosk)

    @prepare_rates
    def calc_rates(self, day, drv):

        p = self.params
        r = self.rates
        s = self.states
        k = self.kiosk

        drv = wdp(day)
        drvTEMP = ((drv.TMIN + drv.TMAX)/2)
        # Development rate of a plant (DVR) depends on daily mean temperature (drv.TEMP) and plant age (DVS).
        r.DVR = self._dev_rate_plant(drvTEMP,s.DVS)

        # Development rate of a fruit (DVRF) depends on temperature and the developmet stage of the fruit.
        # The function to calculate DVRF is applied to each element of s.DVSF
        # DVRF =  [list(map(lambda x: self._dev_rate_fruit(drvTEMP, x), row)) for row in k.DVSF]
        # [list(map(lambda x: print(x), row)) for row in k.DVSF]
        # DVRF =  [(print(row)) for row in k.DVSF]
   
        DVRF =  [list(map(lambda x: self._dev_rate_fruit(drvTEMP, x), row)) for row in k.DVSF]
    
        msg = "Finished rate calculation for %s"
        self.logger.debug(msg % day)

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
        if sDVSF == None:
            rDVRF = None
        else:
            # rDVRF = 0.0181 + math.log(drvTEMP/20) * (0.0392 - 0.213 * sDVSF + 0.415 * sDVSF**2 - 0.24 * sDVSF**3)
            rDVRF = 0.0181 + math.log(drvTEMP/20) * (0.0392 - 0.213 * sDVSF + 0.415 * sDVSF**2 - 0.24 * sDVSF**3)
        return(rDVRF)

    @prepare_states
    def integrate(self,day, delt=1.0):

        p = self.params
        r = self.rates
        s = self.states
        k = self.kiosk
        #回しすぎると超える？

        k.DVSF = list(map(lambda l1, l2: [sum(x) for x in zip(l1, l2)], k.DVSF, k.DVRF))

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
        for i in range(0, int(s.DVS+2)):
            for j in range(0,3):
                if s.DOEL[i][j] == None:
                    s.DOEL[i][j] = day
        i = int(s.DVS) + 3
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
