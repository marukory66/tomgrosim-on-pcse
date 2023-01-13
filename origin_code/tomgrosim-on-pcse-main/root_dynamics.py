# -*- coding: utf-8 -*-
#%%
# Naomichi Fujiuchi (naofujiuchi@gmail.com), April 2022
# This is a derivative work by Fujiuchi (GNU GPL license) from the original work PCSE by Allard de Wit (allard.dewit@wur.nl) (EUPL license).
from copy import deepcopy

from pcse.traitlets import Float, Int, Instance
from pcse.decorators import prepare_rates, prepare_states
from pcse.util import limit, merge_dict, AfgenTrait
from pcse.base import ParamTemplate, StatesTemplate, RatesTemplate, \
    SimulationObject, VariableKiosk
    
class Simple_Root_Dynamics(SimulationObject):

    class Parameters(ParamTemplate):
        ROI = Float(-99.) # Initial root dry mass 
                    
    class RateVariables(RatesTemplate):
        GRRO = Float(-99.) # Growth rate of root dry mass

    class StateVariables(StatesTemplate):
        RO = Float(-99) # Root dry mass

    def initialize(self, day, kiosk, parameters):
        """
        :param day: start date of the simulation
        :param kiosk: variable kiosk of this PCSE  instance
        :param parameters: ParameterProvider object with key/value pairs
        """

        self.params = self.Parameters(parameters)
        self.rates = self.RateVariables(kiosk)
        self.kiosk = kiosk
        
        # INITIAL STATES
        params = self.params
        RO = params.ROI

        self.states = self.StateVariables(kiosk, publish=["RO"],
                                          RO=RO)

    @prepare_rates
    def calc_rates(self, day, drv):
        params = self.params
        rates = self.rates
        k = self.kiosk
        
        rates.GRRO = k.DMI * k.FR # Dry mass partitioned to roots. The partitioning fraction ratio of roots is FR.

    @prepare_states
    def integrate(self, day, delt=1.0):
        rates = self.rates
        states = self.states

        states.RO += rates.GRRO