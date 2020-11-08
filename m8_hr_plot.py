#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
"""
plot module.
plot the results, i.e capacity installed and dispatches.

@author: jinxi
"""

import matplotlib.pyplot as plt
import numpy as np
#from m_main import plot_dispatch ,ts

#width = [
#28,146,65,25,34,128,53,21,24,35,19,7,0,0,0,0
#,256,1027,751,283,104,398,213,72,124,227,163,81,23,15,15,1
#,153,645,434,255,59,268,235,119,264,703,419,138,48,102,10,8
#,16,63,70,73,10,34,33,46,17,52,89,53,1,3,2,0
#]

#print (plot_dispatch)
def fun_plot(plot_dispatch,ylabel,title,yr):
    plot_dispatch.fillna(value=0,inplace=True) ##Fill NA/NaN values with 0.
    
    N = len(plot_dispatch.columns) ## nr of bars.

    rt_coal = plot_dispatch.loc['coal']
    #print(rt_coal)
    rt_gas = plot_dispatch.loc['gas']
    rt_solar= plot_dispatch.loc['solar']
    rt_wind = plot_dispatch.loc['wind']
    rt_CN_baseload = plot_dispatch.loc['CN_baseload']
    rt_biomass = plot_dispatch.loc['biomass']
    

    ymax = plot_dispatch.sum(axis = 0).max() ## for ytick(.)
#    print ('ymax is ' + str(ymax))

    ind = np.arange(N)+ 1    # the x locations for the groups, start from 1 instead of 0.
    width = 1        # the width of the bars.

    p_coal = plt.bar(ind, rt_coal, width,color='saddlebrown')
    p_gas = plt.bar(ind, rt_gas, width, bottom = rt_coal, color='dodgerblue')
    p_solar = plt.bar(ind, rt_solar, width, bottom = rt_gas+rt_coal, color='gold')
    p_wind = plt.bar(ind, rt_wind, width, bottom = rt_solar+rt_gas+rt_coal, color='forestgreen')
    p_CN_baseload = plt.bar(ind, rt_CN_baseload, width, bottom = rt_wind + rt_solar+rt_gas+rt_coal, color='silver')
   
#    p_coal = plt.bar(ind, rt_coal, width,color='saddlebrown')
#    p_gas = plt.bar(ind, rt_gas, width, color='silver')
#    p_solar = plt.bar(ind, rt_solar, width, color='gold')
#    p_wind = plt.bar(ind, rt_wind, width, color='forestgreen')
#    p_CN_baseload = plt.bar(ind, rt_CN_baseload, width, color='silver')
#    
    

    plt.ylabel(str(ylabel))
    plt.title(str(title))
    plt.xticks(ind, fontsize=8)
#    plt.yticks(np.arange(0, ymax, ymax/10))
#    plt.legend((p_CN_baseload[0], p_wind[0],p_solar[0], p_gas[0] ,p_coal[0]), ('CN_baseload','wind','solar', 'gas','coal'), framealpha=0)

    #plt.savefig('figure',dpi=200)
    plt.show()
    
    return p_coal,p_gas,p_solar,p_wind,p_CN_baseload
