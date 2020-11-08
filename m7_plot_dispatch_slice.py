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
from m2_demand_slices import q0_hr_slice,q0t_64
#from m_main import plot_dispatch ,ts

#print (plot_dispatch)
def func_plot_dispatch_slice(plot_dispatch,el_price,title,yr):
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
    # ~ width = np.reshape(q0_hr_slice,(64))/200      # the width of the bars.
    width = 0.95
    fig = plt.figure(figsize=(16,9))
    
    p_coal = plt.bar(ind, rt_coal, width,color='saddlebrown')
    p_gas = plt.bar(ind, rt_gas, width, bottom = rt_coal, color='deepskyblue')
    p_biomass = plt.bar(ind, rt_biomass, width, bottom = rt_gas+rt_coal, color='plum')
    p_solar = plt.bar(ind, rt_solar, width, bottom = rt_gas+rt_coal+rt_biomass, color='gold')
    p_wind = plt.bar(ind, rt_wind, width, bottom = rt_solar+rt_gas+rt_coal+rt_biomass, color='olivedrab')
    p_CN_baseload = plt.bar(ind, rt_CN_baseload, width, bottom = rt_wind + rt_solar+rt_biomass+rt_gas+rt_coal, color='silver')
    
#    p_coal = plt.bar(ind, rt_coal, width,color='saddlebrown')
#    p_gas = plt.bar(ind, rt_gas, width, color='silver')
#    p_solar = plt.bar(ind, rt_solar, width, color='gold')
#    p_wind = plt.bar(ind, rt_wind, width, color='forestgreen')
#    p_CN_baseload = plt.bar(ind, rt_CN_baseload, width, color='silver')
#    
    demand = plt.plot(ind,q0t_64, 'k--') ##plot the demand line as black dashed line.
    # ~ plt.text(x=ind, y=q0t_64, s=el_price)
    i=1
    for a,c in zip(ind,el_price):
        i*=-1
        plt.text(a, ymax+(i*10**6) , str(int(c))+',',fontsize=10,horizontalalignment='center')
    
    
    plt.xticks([r + width for r in range(N+1)], np.reshape(q0_hr_slice,(64)), rotation=90) ##use allocated hours as xlabel.
    # ~ plt.ticklabel_format(axis='y', style='sci', scilimits=(0,3), useMathText=True)
    plt.xlabel('allocated hours')
    plt.ylabel('KW',fontsize=12)
    plt.title(str(title), fontsize=11)

#    plt.yticks(np.arange(0, ymax, ymax/10))
    plt.legend((p_CN_baseload[0],p_wind[0],p_solar[0],p_biomass[0], p_gas[0] ,p_coal[0]), ('CN_baseload','wind','solar',' biomass', 'natural gas','coal'),
     framealpha=0,bbox_to_anchor=(1, 1))
  
    plt.savefig("output/figures/dispath/slice_dispatch\yr"+ str(yr), dpi=600)
    #plt.savefig('figure',dpi=200)
    plt.grid(True,axis='y')
    # ~ plt.show()
    plt.clf()
    plt.close()
    return p_coal,p_gas,p_solar,p_wind,p_CN_baseload, p_biomass
