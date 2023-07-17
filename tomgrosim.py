# -*- coding: utf-8 -*-
#%%
# Naomichi Fujiuchi (naofujiuchi@gmail.com), April 2022
# This is a derivative work by Fujiuchi (GNU GPL license) from the original work PCSE by Allard de Wit (allard.dewit@wur.nl) (EUPL license).
import datetime
import copy

from pcse.traitlets import Float, Int, Instance, Enum, Unicode
from pcse.decorators import prepare_rates, prepare_states
from pcse.base import ParamTemplate, StatesTemplate, RatesTemplate, SimulationObject
from pcse import signals
from pcse import exceptions as exc
from datetime import date
from phenology import DVS_Phenology as Phenology
from partitioning import DVS_Partitioning as Partitioning
from respiration import TOMGROSIM_Maintenance_Respiration as MaintenanceRespiration
from stem_dynamics import Simple_Stem_Dynamics as Stem_Dynamics
from root_dynamics import Simple_Root_Dynamics as Root_Dynamics
from leaf_dynamics import TOMGROSIM_Leaf_Dynamics as Leaf_Dynamics
from storage_organ_dynamics import TOMGROSIM_Storage_Organ_Dynamics as Storage_Organ_Dynamics
import pandas as pd
import math
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

    class Parameters(ParamTemplate):
        CVL = Float(-99.)
        CVO = Float(-99.)
        CVR = Float(-99.)
        CVS = Float(-99.)
        DMII = Float(-99.)
        ASSIMI = Instance(list)


    class StateVariables(StatesTemplate):
        TDM  = Float(-99.) # Total living plant dry mass
        GASST = Float(-99.)
        MREST = Float(-99.)
        DOF = Instance(datetime.date)
        FINISH_TYPE = Unicode(allow_none=True)
        ASA = Float(-99.) # Assimilate pool
        AF = Float(-99.)
        CAF = Float(-99.)
        DMI = Float(-99.) # Dry matter increase
        CVF = Float(-99.)
        DMA = Float(-99.) # Dry mass available for growth
        RGRL = Instance(list)
        GASS = Float(-99.)
        MRES = Float(-99.)
        ASRC = Float(-99.)
        ASSIM = Instance(list)


    class RateVariables(RatesTemplate):
        pass

    def initialize(self, day, kiosk, parvalues):
        print("tomgrosim.py")
        self.params = self.Parameters(parvalues)
        self.kiosk = kiosk
        self.pheno = Phenology(day, kiosk, parvalues)
        self.part = Partitioning(day, kiosk, parvalues)
        self.mres = MaintenanceRespiration(day, kiosk, parvalues)
        self.ro_dynamics = Root_Dynamics(day, kiosk, parvalues)
        self.st_dynamics = Stem_Dynamics(day, kiosk, parvalues)
        self.so_dynamics = Storage_Organ_Dynamics(day, kiosk, parvalues)
        self.lv_dynamics = Leaf_Dynamics(day, kiosk, parvalues)

        # Initial total (living) above-ground biomass of the crop
        TDM = self.kiosk.WLV + self.kiosk.WST + self.kiosk.WSO + self.kiosk.WRO
        DMII = 0.2*TDM
        # TDM = self.kiosk.TWLV + 1 + self.kiosk.TWSO

        # GASS = copy.deepcopy(self.params.GASSL)
        ASSIM = copy.deepcopy(self.params.ASSIMI)

        self.states = self.StateVariables(kiosk,
                                          publish=["CVF","DMI","RGRL","TDM","GASST","MREST","ASA", "AF", "CAF","DMA","ASSIM"],
                                          CVF=None,DMI=DMII,RGRL=[],DMA=None,MRES=None,ASRC=None,GASS=None,ASSIM=ASSIM,
                                          TDM=TDM, GASST=0.0, MREST=0.0,
                                          DOF=None, FINISH_TYPE=None,
                                          ASA=0.0, AF=None, CAF=1.0)

        self._connect_signal(self._on_CROP_FINISH, signal=signals.crop_finish)

    @prepare_rates
    def calc_rates(self, day, drv):
    # def calc_rates(self, day, kiosk, drv):
        print("day",day)
        p = self.params
        r = self.rates
        k = self.kiosk
        self.pheno.calc_rates(day,drv)

        # Relative growth rate (RGR) of plant
        # RGRL is the list of RGRs
        RGR = k.DMI / k.TDM
        k.RGRL.insert(0, RGR)

        # Potential assimilation

        # t_year = day.strftime("%Y")
        # t_month = day.strftime("%m").lstrip("0")
        # t_day = day.strftime("%d").lstrip("0")
        # without_0day = t_year + "/" + t_month + "/" + t_day

        # if day < date(2006,7,1):
        #     #3か月は仮データでシミュレーション上で大きくなるまで待機
        #     #ここで実測光合成量をyamlから取得している
        #     def assim_get(Gass_list,day):
        #         t_year = day.strftime("%Y")
        #         t_month = day.strftime("%m").lstrip("0")
        #         t_day = day.strftime("%d").lstrip("0")
        #         without_0day = t_year + "/" + t_month + "/" + t_day
        #         for row in range(len(Gass_list)):
        #             tmp_day = Gass_list[row][0]
        #             if tmp_day == str(without_0day):
        #                 return Gass_list[row][-1]
        # # k.GASS = self.assim(day, drv) + k.ASA

        # #単位面積当たりの日積算光合成量　[gCH2O m-2 d-1] = チャンバ日積算光合成量　[mol d-1] *30 [gC-H2O mol-1] / 2 [/plant] *p.PD　[plant m-2]
        #     k.GASS = assim_get(k.ASSIM,day) + k.ASA#[gCH2O m-2 d-1]
        #     # print("7月以前",day)
        #     # Respiration
        #     PMRES = self.mres(day, drv)
        #     k.MRES  = min(k.GASS, PMRES)

        #     # Net available assimilates
        #     # k.ASRC  = k.GASS - k.MRES
        #     k.ASRC  = k.GASS

        def ASSIMR(EFF, PGMAX, LAI, SINELV, PARDIR, PARDIF):
            REFGR = 0.5
            SCP = 0.15
            KDIFBL = 0.8
            KDIF = 0.72
            XGAUS3 = [0.112702, 0.5, 0.887298]
            WGAUS3 = [0.277778, 0.444444, 0.277778]
            SINEL = max(0.02, SINELV)
            REFL = (1 - (1 - SCP)**(1/2)) / (1 + (1 - SCP)**(1/2))
            REFPD = REFL * 2 / (1 + 1.6 * SINEL)
            CLUSTF = KDIF / (KDIFBL * (1 - SCP)**(1/2))
            KDIRBL = (0.5 / SINEL) * CLUSTF
            KDIRT = KDIRBL * (1 - SCP)**(1/2)
            T1 = math.exp(-KDIF * LAI)
            T2 = math.exp(-KDIRT * LAI)
            T3 = T1
            CORR1 = (REFL - REFGR) / (REFGR - 1 / REFL) * T1**2
            CORR2 = -REFPD**2 * T2**2
            CORR3 = -REFL**2 * T3**2
            RE1 = (REFL + CORR1 / REFL) / (1 + CORR1)
            RE2 = (REFPD + CORR2 / REFPD) / (1 + CORR2)
            RE3 = (REFL + CORR3 / REFL) / (1 + CORR3)
            TE1 = T1 * (REFL**2 - 1) / (REFL * REFGR - 1) / (1 + CORR1)
            TE2 = T2 * (1 - REFPD**2) / (1 + CORR2)
            TE3 = T3 *(1 - REFL**2) / (1 + CORR3)
            PHIU = REFGR * PARDIR * TE2 / (1 - RE3 * REFGR)
            PGROS = 0
            for i in range(0,3):
                LAIC = LAI * XGAUS3[i]
                PARLDF = (1 - REFL) * KDIF * (PARDIF * (math.exp(-KDIF * LAIC) + CORR1 * math.exp(KDIF * LAIC) / REFL) / (1 + CORR1) + PHIU * (math.exp(KDIF * (LAIC - LAI)) + CORR3 * math.exp(KDIF * (LAI - LAIC)) / REFL) / (1 + CORR3))
                PARLT = (1 - REFPD) * PARDIR * KDIRT * (math.exp(-KDIRT * LAIC) + CORR2 * math.exp(KDIRT * LAIC) / REFPD) / (1 + CORR2)
                PARLDR = (1 - SCP) * PARDIR * KDIRBL * math.exp(-KDIRBL * LAIC)
                PARLSH = PARLDF + (PARLT - PARLDR)
                PARLPP = PARDIR * (1 - SCP) / SINEL
                FSLLA = CLUSTF * math.exp(-KDIRBL * LAIC)
                ASSSH = PGMAX * (1 - math.exp(-EFF * PARLSH / PGMAX))
                ASSSL = 0
                for j in range(0,3):
                    PARLSL = PARLSH + PARLPP * XGAUS3[j]
                    ASSSL = ASSSL + PGMAX * (1 - math.exp(-EFF * PARLSL/ PGMAX)) * WGAUS3[j]
                PGROS = PGROS + ((1 - FSLLA) * ASSSH + FSLLA * ASSSL) * WGAUS3[i]
            PGROS_ = PGROS * LAI
            return PGROS_

        assim_calculation= "C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse_pypl/df_assim_calculation(EFF,PGMAX).csv"
        df_assim_calculation = pd.read_csv(assim_calculation)


        # if day >= date(2006,7,1):
        tmp_GASS = 0
        # hour = list(df_assim_calculation.query('date == "2006/7/1" and h>0')["hour"])
        sday = day.strftime("%Y/%#m/%#d")
        hour = list(df_assim_calculation.query('date == @sday and h>0')["hour"])
        LAI = k.LAI
        for i in hour:
            tmp = (df_assim_calculation.query('date == @sday and hour==@i'))
            SINELV = tmp["h"].iloc[-1]
            EFF = tmp["EFF"].iloc[-1]
            PGMAX = tmp["PGMAX"].iloc[-1]
            PARDIR = tmp["PARDIR"].iloc[-1]
            PARDIF = tmp["PARDIF"].iloc[-1]
            PGROS = ASSIMR(EFF, PGMAX, LAI, SINELV, PARDIR, PARDIF)
            PGROS = PGROS*7200
            tmp_GASS += PGROS
        tmp_GASS = tmp_GASS/1000/44*30
        #mgCO2をgにするために1000で割り
        k.GASS = tmp_GASS
        # print("7月以降",day)
        # print("k.GASS",k.GASS)

        # Respiration
        PMRES = self.mres(day, drv)
        k.MRES  = min(k.GASS, PMRES)

        # Net available assimilates
        k.ASRC  = k.GASS - k.MRES

        # Potential growth rate
        self.so_dynamics.calc_potential(day, drv)
        self.lv_dynamics.calc_potential(day, drv)

        # DM partitioning factors (pf), conversion factor (CVF), dry matter increase (DMI)
        pf = self.part.calc_rates(day, drv)
        k.CVF = 1./((pf.FL/p.CVL + pf.FS/p.CVS + pf.FO/p.CVO) *
                  (1.-pf.FR) + pf.FR/p.CVR)
        k.DMA = k.CVF * k.ASRC #[gDM m-2 d-1]

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
        print("ASA",k.ASA)
        # Assimilate pool (ASA)
        # All sinks derive their assimilates for growth from one common assimilate pool. (Heuvelink, 1996, Ph.D. thesis, p. 239 (Chapter 6.1))
        if k.DMA <= k.TPGR:
            k.DMI = k.DMA
            s.ASA = 0
        else:
            k.DMI = k.TPGR
            s.ASA = (k.DMA - k.TPGR) / k.CVF
        # Cumulative adaptation (CAF) (De Koning, 1994, Ph.D. thesis, p. 144)
        # Relative adaptation factor (AF) is the difference between 1 and the ratio of the actual potential growth rate to the availability of dry matter.
        # The potential growth rate of a fruit adapts to the plant’s amount of dry matter available for growth.
        # -0.03 <= AF <= 0.03
        # The adaptation factro af is assumed to be equal for all organs and, moreover, af is not affected by the organ's develoment stage.
        # Hence, in the model the amount of calculations are reduced when introducing a single scalar type variable that represents the cumulative (over time) adaptation (CAF).
        # 0 < CAF <= 1, initial CAF = 1
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
        # s.TDM = k.TWLV + 1 + k.TWSO + 1
        s.TDM = k.WLV + k.WST + k.WSO + k.WRO


        # total gross assimilation and maintenance respiration
        s.GASST += k.GASS

        s.MREST += k.MRES

    @prepare_states
    def finalize(self, day):

        SimulationObject.finalize(self, day)

    def _on_CROP_FINISH(self, day, finish_type=None):
        """Handler for setting day of finish (DOF) and reason for
        crop finishing (FINISH).
        """
        self._for_finalize["DOF"] = day
        self._for_finalize["FINISH_TYPE"]= finish_type
