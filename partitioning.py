# -*- coding: utf-8 -*-
#%%
# Naomichi Fujiuchi (naofujiuchi@gmail.com), April 2022
# This is a derivative work by Fujiuchi (GNU GPL license) from the original work PCSE by Allard de Wit (allard.dewit@wur.nl) (EUPL license).
from collections import namedtuple
from math import exp

from pcse.traitlets import Float, Int, Instance
from pcse.decorators import prepare_rates, prepare_states
from pcse.base import ParamTemplate, StatesTemplate,RatesTemplate, SimulationObject, VariableKiosk
from pcse import exceptions as exc
from warnings import warn
from pcse.util import AfgenTrait
#%%

# Template for namedtuple containing partitioning factors
class PartioningFactors(namedtuple("partitioning_factors", "FR FL FS FO")):
    pass

class DVS_Partitioning(SimulationObject):
    
    class StateVariables(StatesTemplate):
        FR = Float(-99.)
        FL = Float(-99.)
        FS = Float(-99.)
        FO = Float(-99.)
        PF = Instance(PartioningFactors)
        TPGR = Float(-99.)
        TMPGR = Float(-99.)
        TPGRLV = Float(-99.)
        TMPGRLV = Float(-99.)
        TPGRFR = Float(-99.)
        TMPGRFR = Float(-99.)
        TPGRST = Float(-99.)
        TPGRRO = Float(-99.)

    class RateVariables(RatesTemplate):
        pass

    def initialize(self, day, kiosk, parvalues):

        # self.params = self.Parameters(parvalues)
        self.kiosk = kiosk
        
        FR = 1
        FL = 1
        FS = 1
        FO = 1
        TPGR = 1
        TMPGR = 1
        TPGRLV = 1
        TMPGRLV = 1
        TPGRFR = 1
        TMPGRFR = 1
        TPGRST = 1
        TPGRRO = 1

        # Pack partitioning factors into tuple
        PF = PartioningFactors(FR, FL, FS, FO)
        
        self.states = self.StateVariables(kiosk, publish=["FR","FL","FS","FO","TPGR","TMPGR","TPGRLV","TMPGRLV","TPGRFR","TMPGRFR","TPGRST","TPGRRO"],
                                          FR=FR, FL=FL, FS=FS, FO=FO, PF=PF, 
                                          TPGR=TPGR, TMPGR=TMPGR, 
                                          TPGRLV=TPGRLV, TMPGRLV=TMPGRLV, TPGRFR=TPGRFR, TMPGRFR=TMPGRFR, 
                                          TPGRST=TPGRST, TPGRRO=TPGRRO)
        self.rates = self.RateVariables(kiosk)
        # @prepare_states
        # def integrate(self, day, delt=1.0):
    
    def calc_rates(self,day, drv):
        
        k = self.kiosk
        r = self.rates

        k.TPGRLV = sum(map(sum, k.PGRLV)) # Total potential growth rate of all the leaves
        k.TMPGRLV = sum(map(sum, k.MPGRLV)) # Total potential growth rate of all the leaves
        k.TPGRFR = sum(map(sum, k.PGRFR)) # Total potential growth rate of all the fruits
        k.TMPGRFR = sum(map(sum, k.MPGRFR)) # Total potential growth rate of all the fruits
     
        # print(k.TPGRRO)
        # Partitioning within the vegetative plant part is at 7:3:1.5 for leaves, stem and roots, respectively. (Heuvelink, 1996, Ph.D. thesis, p.239 (Chapter 6.1)). 
        # Therefore, the total potential growth rates of stems and roots are 3/7 and 1.5/7 of that of leaves, respectively.
        # k.TPGRST = k.TPGRLV * 3/7 # Total potential growth rate of stems
        # k.TPGRRO = k.TPGRLV * 1.5/7 # Total potential growhth rate of roots
        # k.TPGR = k.TPGRLV + k.TPGRST + k.TPGRRO + k.TPGRFR # Total potential growth rate of all the organs
        # # print(k.TPGRRO)
        # print(k.TPGR)
        k.TPGRST = 1
        k.TPGRRO = 1
        k.TPGR = 1


        k.FR = k.TPGRRO / k.TPGR
        k.FL = k.TPGRLV / k.TPGR
        k.FS = k.TPGRST / k.TPGR
        k.FO = k.TPGRFR / k.TPGR
        r.PF = PartioningFactors(k.FR, k.FL, k.FS, k.FO)
        #↑注意
        k.TMPGR = k.TMPGRLV + k.TMPGRLV * 3/7 + k.TMPGRLV * 1.5/7 + k.TMPGRFR # Total maximum potential growth rate of all the organs

        return self.rates.PF