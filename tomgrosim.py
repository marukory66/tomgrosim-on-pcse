# -*- coding: utf-8 -*-
#%%
# Naomichi Fujiuchi (naofujiuchi@gmail.com), April 2022
# This is a derivative work by Fujiuchi (GNU GPL license) from the original work PCSE by Allard de Wit (allard.dewit@wur.nl) (EUPL license).
import datetime

from pcse.traitlets import Float, Int, Instance, Enum, Unicode
from pcse.decorators import prepare_rates, prepare_states
from pcse.base import ParamTemplate, StatesTemplate, RatesTemplate, SimulationObject
from pcse import signals
from pcse import exceptions as exc
from datetime import date

"""↓各.を削除"""
from phenology import DVS_Phenology as Phenology
from partitioning import DVS_Partitioning as Partitioning
from respiration import TOMGROSIM_Maintenance_Respiration as MaintenanceRespiration
from stem_dynamics import Simple_Stem_Dynamics as Stem_Dynamics
from root_dynamics import Simple_Root_Dynamics as Root_Dynamics
from leaf_dynamics import TOMGROSIM_Leaf_Dynamics as Leaf_Dynamics
from storage_organ_dynamics import TOMGROSIM_Storage_Organ_Dynamics as Storage_Organ_Dynamics
#%%
# class Tomgrosim(SimulationObject):
class Tomgrosim(SimulationObject):
    
    # sub-model components for crop simulation
    pheno = Instance(SimulationObject)
    part  = Instance(SimulationObject)
    mres  = Instance(SimulationObject)
    lv_dynamics = Instance(SimulationObject)
    st_dynamics = Instance(SimulationObject)
    ro_dynamics = Instance(SimulationObject)
    so_dynamics = Instance(SimulationObject)
    
    #追加
    # assim = Instance(SimulationObject)

    # Parameters, rates and states which are relevant at the main crop
    # simulation level
    class Parameters(ParamTemplate):
        CVL = Float(-99.)
        CVO = Float(-99.)
        CVR = Float(-99.)
        CVS = Float(-99.)

    class StateVariables(StatesTemplate):
        TDM  = Float(-99.) # Total living plant dry mass
        GASST = Float(-99.)
        MREST = Float(-99.)
        CTRAT = Float(-99.)
        CEVST = Float(-99.)
        HI = Float(-99.)
        DOF = Instance(datetime.date)
        FINISH_TYPE = Unicode(allow_none=True)
        ASA = Float(-99.) # Assimilate pool
        AF = Float(-99.)
        CAF = Float(-99.)

        #以下追記
        DMI = Float(-99.) # Dry matter increase
        RGRL = Instance(list)
        CVF = Float(-99.)
        DMA = Float(-99.) # Dry mass available for growth
        RGRL = Instance(list)
        GASS = Float(-99.)
        MRES = Float(-99.)
        ASRC = Float(-99.)

    class RateVariables(RatesTemplate):
        pass
                # DMI = Float(-99.) # Dry matter increase
        
        
    def initialize(self, day, kiosk, parvalues):
        
        print("tomgrosim.py")
        self.params = self.Parameters(parvalues)
        self.kiosk = kiosk

        # Initialize components of the crop
        # self.pheno = Phenology(day, kiosk, parvalues)
        self.pheno = Phenology(day, kiosk)
        self.part = Partitioning(day, kiosk, parvalues)
        self.mres = MaintenanceRespiration(day, kiosk, parvalues)
        self.ro_dynamics = Root_Dynamics(day, kiosk, parvalues)
        self.st_dynamics = Stem_Dynamics(day, kiosk, parvalues)
        self.so_dynamics = Storage_Organ_Dynamics(day, kiosk, parvalues)
        self.lv_dynamics = Leaf_Dynamics(day, kiosk, parvalues)

        #追加
        # self.assim = Phenology(day, kiosk)

        # Initial total (living+dead) above-ground biomass of the crop
        TDM = self.kiosk.TWLV + self.kiosk.ST + self.kiosk.TWSO
        # TDM = self.kiosk.TWLV + self.kiosk.TWST + self.kiosk.TWSO

        list_RGRL = [[0 for i in range(3)] for j in range(20)]
        RGRL = list_RGRL
        CVF = 0.0
        DMI = 1.0
        DMA = 0.0
        GASS = 0
        MRES = 0
        ASRC = 0

        # self.states = self.StateVariables(kiosk,publish=["DMI","RGRL","TDM", "GASST", "MREST", "HI", "ASA", "AF", "CAF"],
        #                                   DMI=DMI,RGRL=RGRL,
        #                                   TDM=TDM, GASST=0.0, MREST=0.0,
        #                                   CTRAT=0.0, CEVST=0.0, HI=0.0,
        #                                   DOF=None, FINISH_TYPE=None, 
        #                                   ASA=0.0, AF=0.0, CAF=1.0)

        self.states = self.StateVariables(kiosk,
                                          publish=["CVF","DMI","RGRL","TDM", "GASST", "MREST", "HI", "ASA", "AF", "CAF","DMA"],
                                          CVF=CVF,DMI=DMI,RGRL=RGRL,DMA=DMA,GASS=GASS,MRES=MRES,ASRC=ASRC,
                                          TDM=TDM, GASST=0.0, MREST=0.0,
                                          CTRAT=0.0, CEVST=0.0, HI=0.0,
                                          DOF=None, FINISH_TYPE=None, 
                                          ASA=0.0, AF=0.0, CAF=1.0)

        
        
        # self.states = self.StateVariables(kiosk,
        #                                   publish=["TDM", "GASST", "MREST", "HI", "ASA", "AF", "CAF"],
        #                                   TDM=TDM, GASST=0.0, MREST=0.0,
        #                                   CTRAT=0.0, CEVST=0.0, HI=0.0,
        #                                   DOF=None, FINISH_TYPE=None, 
        #                                   ASA=0.0, AF=0.0, CAF=1.0)

        # self.rates = self.RateVariables(kiosk, publish=["CVF", "DMI", "RGRL"],
        #                                 CVF=None, DMI=None, RGRL=[0.2])

        self._connect_signal(self._on_CROP_FINISH, signal=signals.crop_finish)
        
    @prepare_rates
    # def calc_rates(self, day, drv, kiosk):
    def calc_rates(self, day, drv):
        
        p = self.params
        # p = self.Parameters(parvalues)
        r = self.rates
        k = self.kiosk
        # print("SSSS",day)
        # print(type(day.month))
        # day = str(day.year) + "," + str(day.month) + "," + str(day.day)

        # Phenology
        # self.pheno.calc_rates(day, drv)
        self.pheno.calc_rates(day,drv)

        # Potential assimilation
        
        # 以下は実際の積算光合成量を直接使用 
        # r.GASS = self.assim(day, drv) + r.ASA

        k.GASS = 1 + 1

        # Respiration
        PMRES = self.mres(day, drv)

        #r.GASSを仮置き
        k.MRES  = min(k.GASS, PMRES)
        # r.MRES  = min(r.GASS, PMRES)

        # Net available assimilates
        
        #r.GASSを仮置き
        k.ASRC  = k.GASS - k.MRES
        # r.ASRC  = r.GASS - r.MRES

        # Potential growth rate
        # self.so_dynamics.calc_potential(kiosk,day, drv)
        self.so_dynamics.calc_potential(day, drv)
        self.lv_dynamics.calc_potential(day, drv)

        # DM partitioning factors (pf), conversion factor (CVF), dry matter increase (DMI)
        # print("CVF",k.CVF)
        
        pf = self.part.calc_rates(day, drv)
       
        #rateは使用できない→kiosk(state)使用
        # r.CVF = 1./((pf.FL/p.CVL + pf.FS/p.CVS + pf.FO/p.CVO) *
        #           (1.-pf.FR) + pf.FR/p.CVR)
        
        k.CVF = 1./((pf.FL/p.CVL + pf.FS/p.CVS + pf.FO/p.CVO) *
                  (1.-pf.FR) + pf.FR/p.CVR)
        
        # r.DMA = r.CVF * r.ASRC
        k.DMA = k.CVF * k.ASRC

        # Relative growth rate (RGR) of plant
        # RGRL is the list of RGRs
        RGR = k.DMI / k.TDM
        k.RGRL.insert(0, RGR)

        self.ro_dynamics.calc_rates(day, drv)
        self.st_dynamics.calc_rates(day, drv)
        self.so_dynamics.calc_rates(day, drv)
        self.lv_dynamics.calc_rates(day, drv)


    @prepare_states
    def integrate(self, day, delt=1.0):
        k = self.kiosk
        r = self.rates
        s = self.states

        # Phenology
        self.pheno.integrate(day, delt)

        # Assimilate pool (ASA)
        # All sinks derive their assimilates for growth from one common assimilate pool. (Heuvelink, 1996, Ph.D. thesis, p. 239 (Chapter 6.1))
        # print("ss",k.DMA)
        # print("sss",k.TPGR)
        
        # TPGRはpartitioningのcalc_rateでpublishしているため仮置き
        k.TPGR = 1

        if k.DMA <= k.TPGR:
            k.DMI = k.DMA
            s.ASA = 0
        else:
            k.DMI = k.TPGR
            s.ASA = (k.DMA - k.TPGR) / k.CVF
        # if r.DMA <= k.TPGR:
        #     r.DMI = r.DMA
        #     s.ASA = 0
        # else:
        #     r.DMI = k.TPGR
        #     s.ASA = (r.DMA - k.TPGR) / r.CVF


        # Cumulative adaptation (CAF) (De Koning, 1994, Ph.D. thesis, p. 144)
        # Relative adaptation factor (AF) is the difference between 1 and the ratio of the actual potential growth rate to the availability of dry matter.
        # The potential growth rate of a fruit adapts to the plant’s amount of dry matter available for growth.
        # -0.03 <= AF <= 0.03
        # The adaptation factro af is assumed to be equal for all organs and, moreover, af is not affected by the organ's develoment stage.
        # Hence, in the model the amount of calculations are reduced when introducing a single scalar type variable that represents the cumulative (over time) adaptation (CAF).
        # 0 < CAF <= 1, initial CAF = 1
        
        # TMPGRはpartitioningのcalc_rateでpublishしているため仮置き
        k.TMPGR = 1
        s.AF = (k.DMA - k.TPGR) / k.TMPGR
        if s.AF < -0.03: 
            s.AF = -0.03
        elif s.AF > 0.03:
            s.AF = 0.03
        s.CAF += s.AF
        if s.CAF < 0.01: 
            s.CAF = 0.01
        elif s.CAF >= 1.00:
            s.CAF = 1.00
 
        # Integrate states on leaves, storage organs, stems and roots
        self.ro_dynamics.integrate(day, delt)
        self.so_dynamics.integrate(day, delt)
        self.st_dynamics.integrate(day, delt)
        self.lv_dynamics.integrate(day, delt)

        # Total living plant dry mass
        #TWROがどこにも定義されていない
        s.TDM = k.TWLV + k.ST + k.TWSO + 1
        # s.TDM = k.TWLV + k.TWST + k.TWSO + k.TWRO

        # total gross assimilation and maintenance respiration 
        s.GASST += k.GASS
        s.MREST += k.MRES
        # s.GASST += r.GASS
        # s.MREST += r.MRES
        
    @prepare_states
    def finalize(self, day):
        
        SimulationObject.finalize(self, day)

    def _on_CROP_FINISH(self, day, finish_type=None):
        """Handler for setting day of finish (DOF) and reason for
        crop finishing (FINISH).
        """
        self._for_finalize["DOF"] = day
        self._for_finalize["FINISH_TYPE"]= finish_type
