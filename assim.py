"""
<p>(Gijzen, 1992) LPHCURを参照した。</p>
<p>
Input: <br>
TLEAF: leaf temperature [℃]<br>
CO2AIR: CO2 concentration [µL L-1] or [µmol mol-1]<br>
</p>
<p>
Output: <br>
EFF: leaf initial light use efficiency [mgCO2 J-1] or [molCO2 molPhoton-1]<br>
PGMAX: leaf gross assim. at light satur. [mgCO2 mLeaf-2 s-1] or [µmolCO2 mLeaf-2 s-1]<br>
</p>

```{r, warning=FALSE, message=FALSE, eval=FALSE}

#はコメントアウト
LHCURの関数作成
関数の形 f <- function(引数){return(戻り値)}
LPHCUR = function(TLEAF, CO2AIR, unit = "g"){ 
  # function that returns a dataframe of EFF and PGMAX
  # If unit == "g", the unit of EFF is [mgCO2 J-1] and the unit of PGMAX is [mgCO2 m-2 s-1]. If unit == "mol", the unit of EFF is [molCO2 molPhoton-1] and the unit of PGMAX is [µmolCO2 m-2 s-1].
  
  RS = 50 # [s m-1]
  RB = 100 # [s m-1]
  Q10RD = 2.0

if文の形 if(条件){処理} else if(){} else {}


  if(unit == "g"){
    EFF0 = 0.017 # [mgCO2 J-1]
    RD20 = 0.05 # [mgCO2 m-2 s-1]
    # Table for tempearture dependence of inverse of carboxylation resistance (m s-1) (Bertin and Heuvelink, 1993)
    
    GCTというdataframe型にT列とGC列があって，これらにC()で入力している
    
    GCT = data.frame(T = c(0, 5, 15, 25, 40, 100), GC = c(0, 0, 0.004, 0.004, 0, 0))
    # Table for temperature dependence of maximal endogenous photosynthetic capacity (mgCO2 m-2 s-1) (Bertin and Heuvelink, 1993)
    PMMT = data.frame(T = c(0, 5, 15, 25, 40, 100), PMM = c(0, 0, 2, 2, 0, 0))
  }else if(unit == "mol"){
    EFF0 = 0.084 # [molCO2 mol-1photon]
    RD20 = 1.136 # [µmolCO2 m-2 s-1]
    # Table for tempearture dependence of inverse of carboxylation resistance (m s-1) (Bertin and Heuvelink, 1993)
    GCT = data.frame(T = c(0, 5, 15, 25, 40, 100), GC = c(0, 0, 0.004, 0.004, 0, 0))
    # Table for temperature dependence of maximal endogenous photosynthetic capacity (µmolCO2 m-2 s-1) (Bertin and Heuvelink, 1993)
    PMMT = data.frame(T = c(0, 5, 15, 25, 40, 100), PMM = c(0, 0, 45, 45, 0, 0))
  }
if文終り

  # Conductance GC is a function of temperature [m s-1] <- ただのInterpolation
  GC = approx(x = GCT$T, y = GCT$GC, xout = TLEAF)$y
  
  # RC is the carboxylation resistance to CO2 assimilation [s m-1]
  if(GC < 0.00001){
    RC = 3 * 10^30 # [s m-1]
  }else{
    RC = 1 / GC # [s m-1]
  }
  
  # Endogenous photosynthetic capacity PMM is a function of temperature
  PMM = approx(x = PMMT$T, y = PMMT$PMM, xout = TLEAF)$y
  
  # CO2 compensation point increases with temperature dependance according to Brroks & Farquhar, 1985
  GAMMA = 42.7 + 1.68 * (TLEAF - 25) + 0.012 * (TLEAF - 25)^2 # [µL L-1]
  

  
  # Reduction of light use efficiency by photorespiration; affected by CO2 concentration
  CO2 = max(CO2AIR, GAMMA) # [µL L-1]
  EFF_ = EFF0 * (CO2 - GAMMA) / (CO2 + 2 * GAMMA) # [mgCO2 J-1]
  
  # Pn,c is maximum as determined by CO2 diffusion. 
  # ALPHA is constant 1.8 converting µLCO2 L−1 (µmolCO2 mol−1) to mgCO2 m−3 or constant 41.6 converting µLCO2 L−1 (µmolCO2 mol−1) to µmolCO2 m−3 at 20℃
  # Stomatal resistance and boundary layer resistance to CO2 are 1.6 and 1.37 times larger than to water vapour, respectively. (Bertin and Heuvelink, 1993) ではRBの係数が1.36となっていたので，1.36を採用した。
  if(unit == "g"){
    ALPHA = 1.8
  }else if(unit == "mol"){
    ALPHA = 41.6
  }
  PNC = ALPHA * (CO2 - GAMMA) / (1.36 * RB + 1.6 * RS + RC)
  
  # PNMAX shows saturation with PNC
  PNMAX = min(PNC, PMM)
  
  # Dark respiration
  RD = RD20 * Q10RD^(0.1 * (TLEAF - 20))
  
  # PGMAX is determined by maximal net assimilation PNMAX and RD
  PGMAX_ = PNMAX + RD
  
  return(data.frame(EFF = EFF_, PGMAX = PGMAX_))
}


二つ目
<p>(Gijzen, 1992) ASSIMRを参照した。</p>
<p>
Input: <br>
EFF: leaf initial light use efficiency [mgCO2 J-1] or [molCO2 molPhoton-1]<br>
PGMAX: leaf gross assim. at light satur. [mgCO2 m-2 s-1] or [µmolCO2 m-2 s-1]<br>
LAI: Leaf Area Index [-]<br>
SINELV: sine of solar elevation [-]<br>
PARDIR: flux direct PAR [J m-2 s-1] or [µmol m-2 s-1]<br>
PARDIF: flux diffse PAR [J m-2 s-1] or [µmol m-2 s-1]<br>
</p>
<p>
Output: <br>
PGROS: canopy instantaneous gross assim. [mgCO2 m-2 s-1] or [µmol m-2 s-1]
</p>

```{r, warning=FALSE, message=FALSE}
ASSIMR = function(EFF, PGMAX, LAI, SINELV, PARDIR, PARDIF){
  # function that returns a dataframe of PGROS
  # If you calculated EFF and PGMAX with the argument "unit = "g"" in the function LPHCUR, you sould use PARDIR and PARDIF with the unit [J m-2 s-1]. If you calculated EFF and PGMAX with the argument "unit = "mol"" in the function LPHCUR, you sould use PARDIR and PARDIF with the unit [µmolPhoton m-2 s-1].

  REFGR = 0.5 # reflection of ground surface [-] (Heuvelink, 1995, Dry matter production in a tomato crop: measurement and simulation. Annals of Botany) のwhite plastic sheetの値
  SCP = 0.15 # scattering coefficient for PAR [-] (Gijzen, 1992)
  KDIFBL = 0.8 # extinction coefficient diffuse light of non-scattering leaves (Black Leaves) [-] (Gijzen, 1992)
  KDIF = 0.72 # extinction coefficient diffuse light [-] (Heuvelink, 1996, p.68. Chapter 3.3)
  XGAUS3 = c(0.112702, 0.5, 0.887298)
  WGAUS3 = c(0.277778, 0.444444, 0.277778)
  # Prevent math overflow
  SINEL = max(0.02, SINELV)
  # Canopy reflection coefficient
  REFL = (1 - (1 - SCP)^(1/2)) / (1 + (1 - SCP)^(1/2))
  REFPD = REFL * 2 / (1 + 1.6 * SINEL) # (Gijzen, 1992) では2*SINELだったけど，Goudriann and van Laar, 1994, equation(6.22) では1.6*SINELなので，後者を採用した。
  # Extinction coefficient for direct conponent (KDIRBL) and total direct flux (KDIRT) and cluster factor
  CLUSTF = KDIF / (KDIFBL * (1 - SCP)^(1/2))
  KDIRBL = (0.5 / SINEL) * CLUSTF
  KDIRT = KDIRBL * (1 - SCP)^(1/2)
  # Section calculating effect of ground reflectance of radiation. Transmissivity T, effective transmissivity TE and effective reflectivity RE for incoming diffuse (1), incoming direct and its diffused components together (2) and reflected diffuse radiation from the ground surface (3) reckoned in upward direction
  T1 = exp(-KDIF * LAI)
  T2 = exp(-KDIRT * LAI)
  T3 = T1
  CORR1 = (REFL - REFGR) / (REFGR - 1 / REFL) * T1^2
  CORR2 = -REFPD^2 * T2^2
  CORR3 = -REFL^2 * T3^2
  RE1 = (REFL + CORR1 / REFL) / (1 + CORR1)
  RE2 = (REFPD + CORR2 / REFPD) / (1 + CORR2)
  RE3 = (REFL + CORR3 / REFL) / (1 + CORR3)
  TE1 = T1 * (REFL^2 - 1) / (REFL * REFGR - 1) / (1 + CORR1)
  TE2 = T2 * (1 - REFPD^2) / (1 + CORR2)
  TE3 = T3 * (1 - REFL^2) / (1 + CORR3)
  # Reflected diffused flux at ground surface originating from direct radiation, including secondary reflection 
  PHIU = REFGR * PARDIR * TE2 / (1 - RE3 * REFGR)
  # selection of canopy depth (LAIC from top)
  PGROS = 0
  for(i in 1:3){
    LAIC = LAI * XGAUS3[i]
    # absorbed fluxes per unit leaf area: diffuse flux, total direct flux, direct component of direct flux.
    PARLDF = (1 - REFL) * KDIF * (PARDIF * (exp(-KDIF * LAIC) + CORR1 * exp(KDIF * LAIC) / REFL) / (1 + CORR1) + PHIU * (exp(KDIF * (LAIC - LAI)) + CORR3 * exp(KDIF * (LAI - LAIC)) / REFL) / (1 + CORR3))
    PARLT = (1 - REFPD) * PARDIR * KDIRT * (exp(-KDIRT * LAIC) + CORR2 * exp(KDIRT * LAIC) / REFPD) / (1 + CORR2)
    PARLDR = (1 - SCP) * PARDIR * KDIRBL * exp(-KDIRBL * LAIC)
    # absorbed fluxes (J mLeaf-2 s-1) for shaded and sunlit leaves
    PARLSH = PARLDF + (PARLT - PARLDR)
    # direct PAR absorbed by leaves perpendicular on direct beam
    PARLPP = PARDIR * (1 - SCP) / SINEL
    # fraction sulint leaf area
    FSLLA = CLUSTF * exp(-KDIRBL * LAIC)
    # assimilation of shaded leaf area
    ASSSH = PGMAX * (1 - exp(-EFF * PARLSH / PGMAX))
    # assimilation of sunlit leaf area
    ASSSL = 0
    for(j in 1:3){
      PARLSL = PARLSH + PARLPP * XGAUS3[j]
      ASSSL = ASSSL + PGMAX * (1 - exp(-EFF * PARLSL/ PGMAX)) * WGAUS3[j]
    }
    PGROS = PGROS + ((1 - FSLLA) * ASSSH + FSLLA * ASSSL) * WGAUS3[i]
  }
  # total gross assimilation
  PGROS_ = PGROS * LAI
  
  return(data.frame(PGROS = PGROS_))
}
```


"""