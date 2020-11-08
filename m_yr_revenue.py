#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  yr_profit.py
#  
#  Copyright 2019 jinxi <jinxi@C18BSEL>
#  


##-----------1.import modules and functions---------------------##
import sys
sys.path.append('C:\PhD_Chalmers\Python\Lib\site-packages') ## adding directory
import pandas as pd
from copy import deepcopy
from m2_demand_slices import q0_hr_slice,q0t,availability_levels_solar,availability_levels_wind
from m3_1_availability import fun_availability
from m3_dispatch_order import fun_rank_dispatch
from m4_demand_supply import fun_demand_supply
from m5_utilization import fun_pp_utilization
from m7_plot import fun_plot
pd.set_option('display.max_columns', 12)


        
df_dispatch = pd.read_excel("input/installed_capacity_with_biomass.xlsx",sheet='sheet1',header=0) 

yr_revenue_series = pd.DataFrame(index=['coal','gas','solar','wind','CN_baseload','biomass'])
 
tick = 0


df_attribute = pd.DataFrame({'running_cost': [2.0, 4.5, 0, 0, 1.0, 6.1], 'emission_intensity': [0.001, 0.00045, 0, 0, 0, 0]},index=['coal', 'gas', 'solar','wind','CN_baseload','biomass']); 


n =len(df_dispatch.columns)#length of columns.

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
    
    df_pp_capacity = df_dispatch.iloc[:,year]
    #print(df_pp_capacity)
    df_pp_pi= pd.concat([df_pp_capacity, df_attribute], axis=1)
    df_pp_pi.rename(columns = {str(year+1):'capacity'}, inplace = True)   
    
    df_pp_pi['plant_type'] = df_pp_pi.index
    df_pp_pi['marginal_cost'] = df_pp_pi['running_cost'] + carbon_tax * df_pp_pi['emission_intensity'] 
      
    df_pp_pi.reset_index(drop=True,inplace=True)
    #print(df_pp_pi)
    
    df_pp_pi['revenue_yr'] = 0
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
                    
                df_pp_pi['capacity_available_KW'] = df_pp_pi.apply(lambda row: fun_availability(row.plant_type,avail_solar,avail_wind),axis=1) * df_pp_pi.capacity
                
                ranked_dispatch = fun_rank_dispatch(df_pp_pi)
                
                eq_production,eq_price,last_supply_type,last_supply_percent = fun_demand_supply(df_pp_pi,ranked_dispatch,demand_level)
                df_pp_pi['utilization'] = df_pp_pi.apply(lambda row: fun_pp_utilization(row.marginal_cost,last_supply_percent,eq_price),axis=1)
                df_pp_pi['dispatched_KWHs'] = df_pp_pi.utilization * df_pp_pi.capacity_available_KW * allocated_hours
                df_pp_pi['revenue'] = df_pp_pi.dispatched_KWHs * (eq_price - df_pp_pi.marginal_cost) 
                
                #print(df_pp_pi)
                df_pp_pi['revenue_yr'] += df_pp_pi.revenue
                                
                tick +=1
                continue
            continue
        continue     
    yr_revenue =  df_pp_pi[['plant_type','revenue_yr']].set_index('plant_type')
    
                
    yr_revenue_series[str(year)] = pd.concat([yr_revenue], axis=1, sort=False)

#yr_revenue_series.to_excel("output/yr_revenue_series_0317.xlsx")
yr_sum_revunue = yr_revenue_series.sum(axis=0)
print(yr_revenue_series)
fun_plot(yr_revenue_series,ylabel='(KWh)',title='yearly revenue from different plants',yr=year) ##plot dispatch for whole 70yr.
