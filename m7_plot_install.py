#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
"""
plot module.
plot the results, i.e capacity installed and dispatches.

@author: jinxi
"""
#  
import matplotlib.pyplot as plt
import numpy as np
#from m_main import plot_installed ,ts

#print (plot_installed)
def func_plot_install(plot_installed,ylabel,title):
    plot_installed.fillna(value=0,inplace=True) ##Fill NA/NaN values with 0.
    
    N = len(plot_installed.columns) ## nr of bars.

    rt_coal = plot_installed.loc['coal']
    #print(rt_coal)
    rt_gas = plot_installed.loc['gas']
    rt_solar= plot_installed.loc['solar']
    rt_wind = plot_installed.loc['wind']
    rt_CN_baseload = plot_installed.loc['CN_baseload']
    # ~ rt_biomass = plot_installed.loc['biomass']

    ymax = plot_installed.sum(axis = 0).max() ## for ytick(.)
#    print ('ymax is ' + str(ymax))

    ind = np.arange(N)+ 1    # the x locations for the groups, start from 1 instead of 0.
    width = 0.95        # the width of the bars.
    fig = plt.figure(figsize=(16,9)) ##set the size of the figure.
    
    p_coal = plt.bar(ind, rt_coal, width,color='saddlebrown')
    p_gas = plt.bar(ind, rt_gas, width, bottom = rt_coal, color='slateblue')
    p_solar = plt.bar(ind, rt_solar, width, bottom = rt_gas+rt_coal, color='gold')
    p_wind = plt.bar(ind, rt_wind, width, bottom = rt_solar+rt_gas+rt_coal, color='olivedrab')
    p_CN_baseload = plt.bar(ind, rt_CN_baseload, width, bottom = rt_wind + rt_solar+rt_gas+rt_coal, color='silver')
    # ~ p_biomass = plt.bar(ind, rt_biomass, width, bottom = rt_wind + rt_solar+rt_gas+rt_coal+rt_CN_baseload, color='coral')
   
    plt.xlabel('year')
    plt.xticks(ind, fontsize=8)
    plt.ylabel(str(ylabel))
    plt.ylim(0,1.8*10**8)
    plt.title(str(title))
    
    # ~ plt.yticks(np.arange(0, ymax, ymax/10))
    plt.ticklabel_format(axis='y', style='sci', scilimits=(0,3), useMathText=True)
    plt.legend((p_CN_baseload[0], p_wind[0],p_solar[0], p_gas[0] ,p_coal[0]), ('CN_baseload','wind','solar', 'gas','coal'), framealpha=0,loc='upper left')
    # ~ plt.savefig("output/figures/installed", dpi=600)
    plt.grid(True)
    plt.show()
    plt.clf()
    plt.close()
    
    return p_coal,p_gas,p_solar,p_wind,p_CN_baseload
