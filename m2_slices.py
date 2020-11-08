## slices



#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
time slices

@author: jinxi
"""

import numpy as np
##low_wind,medium_low_wind,medium_high_wind,high_wind

##low_solar
##medium_low_solar
##medium_high_solar
##high_solar

## low q0
low_q0_hr = np.array([
 (28,146,65,25),
 (34,128,53,21)
,(24,35,19,7)
,(0,0,0,0)
])

##medium_low_q0
med_low_q0_hr = np.array([
 (256,1027,751,283)
,(104,398,213,72)
,(124,227,163,81)
,(23,15,15,1)
])
##medium_high_q0

med_high_q0_hr = np.array([
 (153,645,434,255)
,(59,268,235,119)
,(264,703,419,138)
,(48,102,10,8)
])

##high_q0
high_q0_hr = np.array([
 (16,63,70,73)
,(10,34,33,46)
,(17,52,89,53)
,(1,3,2,0)
])

demand_level = [37306*10**3, 47610*10**3, 63240*10**3, 71555*10**3]##KW
solar_availability = [0, 0.05, 0.35, 0.7]
wind_availability = [0.05,0.2, 0.45, 0.7]

# =========================================================
## transfor above 4 parameters into 64*1 numpy array.

slice_hrs = np.array([low_q0_hr, med_low_q0_hr, med_high_q0_hr, high_q0_hr]).reshape(64) ##hour slices.
demand_64 =  np.repeat(demand_level,16)##demand of 64 slices.
solar_level = np.repeat(list(solar_availability)*4,4) ##make into 64 slices.
wind_level = np.array(list(wind_availability)*16)##make into 64 slices.

# ~ print(slice_hrs)
# ~ print(q0t_64)
# ~ print(availability_levels_solar)
# ~ print(availability_levels_wind)
