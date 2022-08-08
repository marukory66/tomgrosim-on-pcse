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
    
    # class RateVariables(StatesTemplate):
    #     FR = Float(-99.)
    #     FL = Float(-99.)
    #     FS = Float(-99.)
    #     FO = Float(-99.)
    #     PF = Instance(PartioningFactors)
    #     TPGR = Float(-99.)
    #     TMPGR = Float(-99.)
    #     TPGRLV = Float(-99.)
    #     TMPGRLV = Float(-99.)
    #     TPGRFR = Float(-99.)
    #     TMPGRFR = Float(-99.)
    #     TPGRST = Float(-99.)
    #     TPGRRO = Float(-99.)

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
        
        FR = 0.
        FL = 0.
        FS = 0.
        FO = 0.
        TPGR = 0.
        TMPGR = 0.
        TPGRLV = 0.
        TMPGRLV = 0.
        TPGRFR = 0.
        TMPGRFR = 0.
        TPGRST = 0.
        TPGRRO = 0.

        # Pack partitioning factors into tuple
        PF = PartioningFactors(FR, FL, FS, FO)
        
        # Initial states
        self.states = self.StateVariables(kiosk, publish=["FR","FL","FS","FO","TPGR","TPGRLV","TMPGRLV","TPGRFR","TMPGRFR"],
                                          FR=FR, FL=FL, FS=FS, FO=FO, PF=PF, 
                                          TPGR=None, TMPGR=None, 
                                          TPGRLV=None, TMPGRLV=None, TPGRFR=None, TMPGRFR=None, 
                                          TPGRST=None, TPGRRO=None)

        # Initial rates
        # self.rates = self.RateVariables(kiosk, publish=["FR","FL","FS","FO","TPGR","TPGRLV","TMPGRLV","TPGRFR","TMPGRFR"],
        #                                   FR=FR, FL=FL, FS=FS, FO=FO, PF=PF, 
        #                                   TPGR=None, TMPGR=None, 
        #                                   TPGRLV=None, TMPGRLV=None, TPGRFR=None, TMPGRFR=None, 
        #                                   TPGRST=None, TPGRRO=None)
        self.rates = self.RateVariables(kiosk)
    # @prepare_states
    # def integrate(self, day, delt=1.0):
    
    def calc_rates(self,day, drv):
        
        k = self.kiosk
        r = self.rates

        #PGRLV等のrateは他の.pyからkiosk経由で持ってくる
        #kioskは

        # r.TPGRLV = sum(map(sum, k.PGRLV)) # Total potential growth rate of all the leaves
        # r.TMPGRLV = sum(map(sum, k.MPGRLV)) # Total potential growth rate of all the leaves
        # r.TPGRFR = sum(map(sum, k.PGRFR)) # Total potential growth rate of all the fruits
        # r.TMPGRFR = sum(map(sum, k.MPGRFR)) # Total potential growth rate of all the fruits
        
        #簡単な式で仮置き
        sample = [1,2,3,4]
        r.TPGRLV = sum(sample) # Total potential growth rate of all the leaves
        r.TMPGRLV = sum(sample) # Total potential growth rate of all the leaves
        r.TPGRFR = sum(sample) # Total potential growth rate of all the fruits
        r.TMPGRFR = sum(sample) # Total potential growth rate of all the fruits
        # print(r.TMPGRFR)


        # Partitioning within the vegetative plant part is at 7:3:1.5 for leaves, stem and roots, respectively. (Heuvelink, 1996, Ph.D. thesis, p.239 (Chapter 6.1)). 
        # Therefore, the total potential growth rates of stems and roots are 3/7 and 1.5/7 of that of leaves, respectively.
        r.TPGRST = r.TPGRLV * 3/7 # Total potential growth rate of stems
        r.TPGRRO = r.TPGRLV * 1.5/7 # Total potential growhth rate of roots
        r.TPGR = r.TPGRLV + r.TPGRST + r.TPGRRO + r.TPGRFR # Total potential growth rate of all the organs
        r.FR = r.TPGRRO / r.TPGR
        r.FL = r.TPGRLV / r.TPGR
        r.FS = r.TPGRST / r.TPGR
        r.FO = r.TPGRFR / r.TPGR
        r.PF = PartioningFactors(r.FR, r.FL, r.FS, r.FO)

        r.TMPGR = r.TMPGRLV + r.TMPGRLV * 3/7 + r.TMPGRLV * 1.5/7 + r.TMPGRFR # Total maximum potential growth rate of all the organs

        return self.rates.PF
