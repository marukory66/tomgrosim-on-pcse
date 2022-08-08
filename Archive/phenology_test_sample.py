#%%
from pcse.crop import phenology,leaf_dynamics,respiration,partitioning,wofost7
# from  pcse.crop.phenology import DVS_Phenology as Phenology
from pcse.base import SimulationObject , VariableKiosk, AncillaryObject,StatesTemplate,WeatherDataProvider
from pcse.traitlets import Float, Integer, Instance
from datetime import date
# from pcse.crop import DVS_Phenology
import numpy as np
import copy
from pcse.fileinput import ExcelWeatherDataProvider
#%%
from maru_phenology import DVS_Phenology as phenology2
#%%

# weatherfile = os.path.join(data_dir, 'meteo', 'nl1.xls')

weatherfile = os.path.join("C:/Users/maruko/OneDrive - 愛媛大学 (1)/02_PCSE/tomgrosim-on-pcse/nl1.xlsx")
wdp = ExcelWeatherDataProvider(weatherfile) # daily weather observation
    
drv = wdp(date(2007,7,3))
print(drv)
print(type((drv.TMAX + drv.TMIN)/2))
kiosk = VariableKiosk()
# print(type(drvTEMP))


#%%


# pheno = phenology(day=date(
# 2007,7,3), kiosk=kiosk)
pheno = phenology2(day=date(2007,7,3), kiosk=kiosk)
# print(pheno)
# ph = pheno.calc_rates(day=date(2007,7,3), drv=drv)
pheno.calc_rates(day=date(2007,7,3), drv=drv,kiosk=kiosk)

# print(ph)



#%%
import math

drvTEMP = 16

class aa():
        
    # def asa(self):
        # DVRF = [list(map(self._dev_rate_fruit(row) , [2,3,4]))]
        # print(DVRF())
    def asa(self):
        DVRF = [list(map(self._dev_rate_fruit, [drvTEMP,drvTEMP,drvTEMP] , [2,3,4]))]
        print(DVRF)
    def _dev_rate_fruit(self, drv_temp, sDVSF):
    # Development rate of a fruit (DVRF) depends on temperature and the developmet stage of the fruit.
    # De Koning (1994, Ph.D. thesis) (and Heuvelink (1996, Annals of Botany)) used the following equation for DVRF. It described fruit growth period in cv. Counter quite well (unpublished research, Heuvelink, 1996).
        rDVRF = 0.0181 + math.log(drvTEMP/20) * (0.0392 - 0.213 * sDVSF + 0.415 * sDVSF**2 - 0.24 * sDVSF**3)
        return(rDVRF)
        
            
a1 = aa()

print(a1.asa())


#%%
DVSF = [3,4,5]
drvTEMP = 1

drvTEMP_list = copy.deepcopy(DVSF)
drvTEMP_list = [drvTEMP for i ,w in enumerate(drvTEMP_list)]
print(drvTEMP_list)

#%%



DVSF = list(map(lambda l1, l2: [sum(x) for x in zip(l1, l2)], DVSF, DVRF))






#%%


import math


class aa():
        
    
    
    DVRF = [list(map(_dev_rate_fruit(drvTEMP,ro) ,[2,3,4]))]
    print(DVRF)

    def _dev_rate_fruit(self,drvTEMP, sDVSF):
    # Development rate of a fruit (DVRF) depends on temperature and the developmet stage of the fruit.
    # De Koning (1994, Ph.D. thesis) (and Heuvelink (1996, Annals of Botany)) used the following equation for DVRF. It described fruit growth period in cv. Counter quite well (unpublished research, Heuvelink, 1996).
        rDVRF = 0.0181 + math.log(drvTEMP/20) * (0.0392 - 0.213 * sDVSF + 0.415 * sDVSF**2 - 0.24 * sDVSF**3)
        return(rDVRF)
            
a = aa()

a.asa






#%%
import math

ssDVSF = [2,3,4]
drvTEMP =16
sDVSF = 1


# DVRF = [list(map(lambda x: _dev_rate_fruit(drvTEMP, x), ssDVSF))]
# DVRF = [list(map(lambda x : _dev_rate_fruit(drvTEMP, x), ssDVSF))]

DVRF = [_dev_rate_fruit(drvTEMP, row) for row in [2,3,4]]


# DVRF = (lambda x: self._dev_rate_fruit(drvTEMP, x))

# DVRF = [(lambda x: self._dev_rate_fruit(drvTEMP, x))]
# DVRF = [(map(lambda x: self._dev_rate_fruit(drvTEMP, x), row)) for row in [2,3,4]]
# DVRF = [(map(lambda x: self._dev_rate_fruit(drvTEMP, x), [2,3,4]))]

# DVRF = [ row for row in [2,3,4]]



print(DVRF)

def _dev_rate_fruit(self,drvTEMP, sDVSF):
        # Development rate of a fruit (DVRF) depends on temperature and the developmet stage of the fruit.
        # De Koning (1994, Ph.D. thesis) (and Heuvelink (1996, Annals of Botany)) used the following equation for DVRF. It described fruit growth period in cv. Counter quite well (unpublished research, Heuvelink, 1996).
        rDVRF = 0.0181 + math.log(drvTEMP/20) * (0.0392 - 0.213 * sDVSF + 0.415 * sDVSF**2 - 0.24 * sDVSF**3)
        return(rDVRF)



#%%

import math

print(math.log(16/-20) )



#%%
import math
def _dev_rate_plant(drvTEMP, sDVS):
    rDVR = -0.286 + 0.1454 * math.log(drvTEMP) - 0.001 * sDVS
    return(rDVR)

_dev_rate_plant(16, 1)


#%%


lists = [["None" for i in range(4)] for j in range(5)]


# lists[0][0] = 1
# lists[0][0] = "{0:%Y/%m/%d}".format(date(2003,7,3))



list_DVSF = list()
list_DOEL = list()
list_DOEF = list()
list_DOHL = list()
list_DOHF = list()

list_DVSF = copy.deepcopy(lists)
list_DOEL = copy.deepcopy(lists)
list_DOEF = copy.deepcopy(lists)
list_DOHL = copy.deepcopy(lists)
list_DOHF = copy.deepcopy(lists)

list_DVSF[0][0] = 1
#実が収穫する時には葉は3果房上分はあるからそれに対応できるように，2日ずつずれて葉が出る
for i in range(20):
    print(i,ii)
    i =+  1
    ii = i
    # if i == 3:
    #     ii=+1
    #     i = 0
    #     list_DOEL[ii][i] = "{0:%Y/%m/%d}".format(date(2003,7,i+3))



list_DOEF[0][0] = "{0:%Y/%m/%d}".format(date(2003,7,3))
list_DOHL[0][0] = lists
list_DOHF[0][0] = lists

print(list_DOEL)


#%%
# for index in range(20):
#     i_index= index//4
#     ii_index = index % 4
#     list_DOEL[i_index][ii_index] = "{0:%Y/%m/%d}".format(date(2003,7,index+2))
# print(list_DOEL)

for index in range(20):
    i_index= index//4
    ii_index = index % 4
    print(i_index)
    list_DOEL[i_index][ii_index] = "{0:%Y/%m/%d}".format(date(2003,7,index-10))
print(list_DOEF)






#%%
kiosk = VariableKiosk()
#直接phenologyに書き込んで実行
# class phenology(SimulationObject):
    # DVS = Float(-99.)
    # DVSF = Instance(list)
    # DOEL = Instance(list)
    # DOEF = Instance(list)
    # DOHL = Instance(list)
    # DOHF = Instance(list)


pheno = phenology(day=date(2003,7,3), kiosk=kiosk)
#%%









#%%
K = VariableKiosk()

# class StateVariables(StatesTemplate):
#     StateA = Float(-99.)
#     StateB = Integer(-99.)
#     StateC = Instance(date)
# s1 = StateVariables(k, publish=["StateA","StateB"], StateA=0., StateB=7, StateC=date(2003,7,3))

# class DVS_Phenology(SimulationObjec):
#     parvalues = Float(-99.)
# class phenology():
#     parvalues = {}
#     day =  Instance(date)
#     kiosk = VariableKiosk()

# pheno = phenology(day=date(2003,7,3),kisok=VariableKiosk(),parvalues={"A" :1., "B" :-99, "C":2.45})
weatherdataprovider = Instance(WeatherDataProvider)

drv = weatherdataprovider(date(2003,7,3))
calc_rates = Instance(phenology.calc_rates)
pheno = phenology(day,kisok,parvalues)
calc_pheno = pheno.calc_rate(date(2003,7,3),drv)
print(pheno)





# a = DVS_Phenology((2003,7,3),k)

# wofost7で　dvs_phenology(day,kiosk,parvalus)

print(a)

# %%
