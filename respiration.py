# -*- coding: utf-8 -*-
#%%
# Naomichi Fujiuchi (naofujiuchi@gmail.com), April 2022
# This is a derivative work by Fujiuchi (GNU GPL license) from the original work PCSE by Allard de Wit (allard.dewit@wur.nl) (EUPL license).
from math import exp
from collections import deque

from pcse.traitlets import Float, Int, Instance, Dict
from pcse.decorators import prepare_rates, prepare_states
from pcse.base import ParamTemplate, SimulationObject, RatesTemplate, StatesTemplate
from pcse.util import AfgenTrait
#%%
class TOMGROSIM_Maintenance_Respiration(SimulationObject):

    class Parameters(ParamTemplate):
        Q10 = Float(-99.)
        RMR = Float(-99.)
        RML = Float(-99.)
        RMS = Float(-99.)
        RMO = Float(-99.)
        # RFSETB = AfgenTrait()
        COEFRGR = Float(-99.)
        # RGR = Float(-99.)


    class RateVariables(RatesTemplate):
        pass

    class StateVariables(StatesTemplate):
        RGR = Float(-99.)


    def initialize(self, day, kiosk, parvalues):
        self.params = self.Parameters(parvalues)
        self.rates = self.RateVariables(kiosk)
        self.kiosk = kiosk
        self.states = self.StateVariables(kiosk,publish=["RGR"],RGR=None)
        self.rates = self.RateVariables(kiosk)


    def __call__(self, day, drv):
        p = self.params
        r = self.rates
        kk = self.kiosk

        RMRES = (p.RMR * kk["WRO"] +
                 p.RML * kk["WLV"] +
                 p.RMS * kk["WST"] +
                 p.RMO * kk["WSO"])
        TEFF = p.Q10**((drv.TEMP-25.)/10.)

        # The maintenance respiration was corrected by temperature and RGR (Heuvelink, 1995, Annals of Botany)
        # The correction by RGR is similar to the correction for senescence using RFSETB as RMRES *= p.RFSETB(kk["DVS"])
        # RGR is list object made in wofost.py. Calculate averaged RGR for the last 1 week = average of the first 7 RGRs in the list.

        # kk.RGR = sum(kk.RGRL[0:6]) / len(kk.RGRL[0:6])
        kk.RGR = 1.0
        kk.PMRES = RMRES * TEFF * (1 - exp(-p.COEFRGR * kk.RGR))
        return kk.PMRES
