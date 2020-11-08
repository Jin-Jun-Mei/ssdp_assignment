#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# yearly_dispatch.py
#  
#  Copyright 2019 jinxi <jinxi@C18BSEL>
#  

##-----------1.import modules and functions---------------------##
import sys
sys.path.append('C:\PhD_Chalmers\Python\Lib\site-packages') ## adding directory
import pandas as pd
import numpy as np

from m1_Class_Plants import pp_list
from m2_demand_slices import q0_hr_slice,q0t,availability_levels_solar,availability_levels_wind
from m3_1_availability import fun_availability
from m3_2_dispatch_order import fun_rank_dispatch
from m4_demand_supply import fun_demand_supply
from m5_utilization import fun_pp_utilization
from m7_plot import fun_plot
pd.set_option('display.max_columns', 12)
pd.options.mode.chained_assignment = None


        
df_installed = pd.read_excel("output\installed_capacity_6.1_90000.xlsx",header=0,index_col=0) 
df_installed.fillna(value=0,inplace=True)
n =len(df_installed.columns)#length of columns.
df_installed.set_axis(np.array(['capacity']*n), axis='columns', inplace=True) ##rename column name to 'capacity'.

dispatched_yr_series = pd.DataFrame(index=[pp.plant_type for pp in pp_list])



#df_attribute = pd.DataFrame({'running_cost': [2.0, 4.5, 0, 0, 1.0,6.1], 'emission_intensity': [0.001, 0.00045, 0, 0, 0,0]},index=['coal', 'gas', 'solar','wind','CN_baseload','biomass']); 
df_attribute = pd.DataFrame({'running_cost': [pp.running_cost for pp in pp_list], 
'emission_intensity': [pp.emission_intensity for pp in pp_list]},index=[pp.plant_type for pp in pp_list])
df_pp_pi = pd.concat([df_attribute,df_installed], axis=1, sort=True, copy=False )##concat two df.
df_pp_pi.reset_index(level=0, inplace=True)## reset index
df_pp_pi.rename({'index':'plant_type'}, axis='columns',inplace=True) ##rename column name.


print(df_pp_pi)

for year in range(n):
    print('\n' +'-----the year is: '+ str(year))
    # =======================================================
    # set carbon_tax
    if year <= 10:
        carbon_tax = 0  ## carbon tax is 0 before year 10.
    elif 10 <= year <= 50:
        carbon_tax = 250 * year - 2500 ## from year 10 to 50, carbon tax increases linearly to 10000 cent/ton.
    else:
        carbon_tax = 10000   ## after year 50, carbon tax stays at 10000 cent/ton.
    # =======================================================
    df_pp = df_pp_pi.iloc[:,[0,1,2,year+3]]
    #df_pp_capacity = df_dispatch.iloc[:,year]
    #print(df_pp_capacity)
    df_pp['marginal_cost'] = df_pp['running_cost'] + carbon_tax * df_pp['emission_intensity'] 
      
    #df_pp.reset_index(drop=True,inplace=True)
    #print(df_pp_pi)
    
    df_pp['dispatched_yr'] = 0
    for q0 in range(len(q0t)): ##length is 4, loop through.
        demand_level = q0t[q0]
        for solar_index in range(len(availability_levels_solar)):##4 levels of solar availability.
            avail_solar = availability_levels_solar[solar_index]
            for wind_index in range(len(availability_levels_wind)):
                avail_wind = availability_levels_wind[wind_index]
                allocated_hours = q0_hr_slice[q0][solar_index][wind_index] ##  hours in current slice.
                # =======================================================
                #print('\n' +'-----new slice: '+ str(allocated_hours) + '(hours)----- ')
                
                #print('the demand reference q0 is: ' + str(demand_level))
                #print('The availability of solar is : ' + str (avail_solar))
                #print('The availability of wind is : ' + str (avail_wind))
                # ~ print(df_pp)    
                df_pp['capacity_available_KW'] = df_pp.apply(lambda row: fun_availability(row.plant_type,avail_solar,avail_wind),axis=1) * df_pp.capacity
                
                ranked_dispatch = fun_rank_dispatch(df_pp)
                
                eq_production,eq_price,last_supply_type,last_supply_percent = fun_demand_supply(df_pp,ranked_dispatch,demand_level)
                df_pp['utilization'] = df_pp.apply(lambda row: fun_pp_utilization(row.marginal_cost,last_supply_percent,eq_price),axis=1)
                df_pp['dispatched_KWHs'] = df_pp.utilization * df_pp.capacity_available_KW * allocated_hours
                #print(df_pp_pi)
                df_pp['dispatched_yr'] += df_pp.dispatched_KWHs
                                
              
                continue
            continue
        continue     
    yr_dispatch =  df_pp[['plant_type','dispatched_yr']].set_index('plant_type')
    
                
    dispatched_yr_series[str(year)] = pd.concat([yr_dispatch], axis=1, sort=False)

#dispatched_yr_series.to_excel("output\yr_dispatched_series_20190401.xlsx")     
#print(dispatched_series)
fun_plot(dispatched_yr_series,ylabel='(KWh)',title='electricity dispached (KWh)',yr=year) ##plot dispatch for whole 70yr.
