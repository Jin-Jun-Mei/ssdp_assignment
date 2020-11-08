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

q0_hr_slice = np.array([low_q0_hr, med_low_q0_hr, med_high_q0_hr, high_q0_hr])
q0t = np.array([37306*10**3, 47610*10**3, 63240*10**3, 71555*10**3])##KW
q0t_64 =  np.repeat(q0t,16)##demand of 64 slices.
# ~ print(q0_hr_slice)


availability_levels_solar =np.array([0, 0.05, 0.35, 0.7])##low_solar,medium_low_solar,medium_high_solar,high_solar.

availability_levels_wind = np.array([0.05,0.2, 0.45, 0.7])##low_wind,medium_low_wind,medium_high_wind,high_wind.
