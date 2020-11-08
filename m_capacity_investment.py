#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  main.py
# =============================================================================
import sys
sys.path.append('C:\PhD_Chalmers\Python\Lib\site-packages') ## adding directory
import pandas as pd
import datetime
import pdb
import numpy as np
#import time
#from openpyxl import Workbook
#wb = Workbook()  
#ws = wb.active 
from m0_import_pp import comp0_initial_PP as df_pp
from m1_Class_Plants import pp_list#,biomass
from m6_decison_making_payback_t import fun_decision_making
from m7_plot_install import func_plot_install
pd.set_option('display.precision',3) ##dismal digits.
pd.set_option('display.max_columns', 12)
pd.options.mode.chained_assignment = None

# =============================================================================
#t6_start = time.perf_counter() 

r=0.08
tot_time_step = 70

investment_list = []
ts = 0
rounds = 0
# ~ tick = 0
installed_capacity_series = pd.DataFrame(index=[pp.plant_type for pp in pp_list]) ##for plotting.index =['coal','gas','solar','wind','CN_baseload','biomass'].

investment_series = []

# ~ print("running cost of biomass is  " + str(biomass.running_cost)+ '(cent/kwh)')

while ts < tot_time_step:
    df_pp.reset_index(drop=True,inplace=True) ## reset the index
    print('\n' + 'tot=' + str(tot_time_step) +'------Current year is ' + str(ts))
    # ~ print('rounds = ' + str(rounds))
    # ~ print('the df_pp is ')
    # ~ print(df_pp[['name','plant_type','lifetime_remain']])
    # ~ dicommision_list = pd.DataFrame()
    
    investment_list = []
    count_invest_pp = {'coal':0,'gas':0,'wind':0,'solar':0,'CN_baseload':0}
# =============================================================================
#   1.set carbon tax (cent/ton co2), and get the marginal costs.
    if ts <= 10:
        carbon_tax = 0  ## carbon tax is 0 before year 10.
    elif 10 <= ts <= 50:
        carbon_tax = 250 * ts - 2500 ## from year 10 to 50, carbon tax increases linearly to 10000 cent/ton.
    else:
        carbon_tax = 10000   ## after year 50, carbon tax stays at 10000 cent/ton.
    
    df_pp['marginal_cost'] = df_pp['running_cost'] + carbon_tax * df_pp['emission_intensity'] 

# =============================================================================
#   2.check decommission and lifetime -1.
    df_pp.lifetime_remain -= 1 ## the lifetime of each plant is subtract by 1. 
    # ~ df_pp.reset_index(drop=True,inplace=True) ## reset the index
    if (df_pp['lifetime_remain']==0).any(): ##if any plant reaches end of the lifetime.
        dicommision_list = df_pp[df_pp['lifetime_remain']==0].sample(frac=1) ##list the to-be-retire pp to a new df, and shuffle the order by .sample()
        print('dicommision_list of current year:')
        print(dicommision_list[['name','plant_type','lifetime_remain']])
    
    # ~ pdb.set_trace() ##set breakpoit.
    # ~ print(dicommision_list)
# =============================================================================
#   3.Making invest decisions.
    # ~ df_pp.sort_values(by=['lifetime_remain'], ascending=False,inplace=True) ## sort the df by 'lifetime_remain'.
    while True:
        if dicommision_list.size >0:
            print(dicommision_list.index[-1])
            df_pp.drop(dicommision_list.index[-1], axis=0, inplace=True) ## drop only one retiring plant each time.
            dicommision_list.drop(dicommision_list.index[-1],axis=0, inplace=True)
        print('\n'+'dicommision_list afer drop ')
        print(df_pp[['name','plant_type','lifetime_remain']])
        # ~ else:
            # ~ break
        # ~ pdb.set_trace()
        invest_made = fun_decision_making(df_pp,carbon_tax,r) ##investment function: take investment decisions.
        if invest_made is not None:
            # ~ print('rounds = ' + str(rounds)+'\n')
            # ~ print('\n' + 'the invest_made is ')
            # ~ print(invest_made['plant_type'])
#            investment_list.append(invest_made['plant_type'])
            rounds += 1 ##stay in the current yr, to check possible further investment.
            df_pp = df_pp.append(invest_made,ignore_index=False,sort=False)## append new pp to df.
            # ~ print('\n'+'lifetime_remain of pp ')
            aa = df_pp[['plant_type','lifetime_remain']].sort_values(by=['lifetime_remain'])
            # ~ print(aa.head(n=5) )
            # ~ print(df_pp[['plant_type','lifetime_remain']])
            count_invest_pp[invest_made.plant_type.item()] += 1
            continue
        
        if (df_pp['lifetime_remain']==0).any():##if more pp needs to be retired this year.
            print('yes')
            continue
            # ~ (df_pp['lifetime_remain']==0).any(): ##check whether any more plant needs to be removed.
        else:
            ts +=1 ##move to next year
            rounds = 0
            break 
                
    # ~ pdb.set_trace() ##set breakpoit.     
#    print('\n' + 'the total capacity now is ')
#    print(df_pp['capacity'].sum(axis = 0, skipna = True))  
    # =========================================
    installed_capacity = df_pp[['plant_type','capacity']].set_index('plant_type')##for plotting in main module.
    installed_capacity = installed_capacity.groupby(['plant_type']).sum()##sum capacity from the same type.
    installed_capacity_series[str(ts)]= pd.concat([installed_capacity], axis=1, sort=False)
    #print(count_invest_pp)
    investment_series.append(count_invest_pp)
    continue    
pp_invest_nr = pd.DataFrame(investment_series)        
#print('(main module)'+'\n'+'-the total investment result is ' + str(wb))

#t6_stop = time.perf_counter()
#t6 = t6_stop-t6_start
#print('the total elapsed time is ' + str(t6))

# ==================================================================#
##export the results
today = datetime.date.today()##year-month-day

installed_capacity_series.to_excel("output/tables/installed/installed_capacity_payback_12.5_"+  str(today) +".xlsx")  ##export the results as input for dispatch calculation.
pp_invest_nr.to_excel("output/tables/installed/pp_invest_nr_payback_12.5_"+ str(today) + ".xlsx")  ##export the results as input for dispatch calculation.

# ==================================================================#
##plot the result.
func_plot_install(installed_capacity_series,ylabel='Capacity Installed (KW)',title='Installed Capacity(KW)payback_12.5_')  
