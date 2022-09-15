# -*- coding: utf-8 -*-
#%%
# Naomichi Fujiuchi (naofujiuchi@gmail.com), April 2022
# This is a derivative work by Fujiuchi (GNU GPL license) from the original work PCSE by Allard de Wit (allard.dewit@wur.nl) (EUPL license).
from pcse.traitlets import Float, Int, Instance
from pcse.decorators import prepare_rates, prepare_states
from pcse.util import limit, AfgenTrait
from pcse.base import ParamTemplate, StatesTemplate, RatesTemplate, \
    SimulationObject, VariableKiosk

class Simple_Stem_Dynamics(SimulationObject):

    class Parameters(ParamTemplate):
        STI = Float(-99.) # Initial stem dry mass 
                    
    class RateVariables(RatesTemplate):
        GRST = Float(-99.) # Growth rate of stem dry mass

    class StateVariables(StatesTemplate):
        ST = Float(-99) # Stem dry mass

    def initialize(self, day, kiosk, parameters):

        self.params = self.Parameters(parameters)
        self.rates = self.RateVariables(kiosk)
        self.kiosk = kiosk
        
        # INITIAL STATES
        params = self.params
        ST = params.STI

        self.states = self.StateVariables(kiosk, publish=["ST"],
                                          ST=ST)

    @prepare_rates
    def calc_rates(self,day, drv):
        rates = self.rates
        k = self.kiosk

        rates.GRST = k.DMI * k.FS # Dry mass partitioned to stems. The partitioning fraction ratio of stems is FS.

    @prepare_states
    def integrate(self, day, delt=1.0):
        rates = self.rates
        states = self.states

        states.ST += rates.GRST
