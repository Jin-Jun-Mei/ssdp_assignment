#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
m6_fun_decision_making

@author: jinxi
"""

#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  m8_decision_making.py
#  
# 

##-----------1.import modules and functions---------------------##
#import sys
#sys.path.append('C:\PhD_Chalmers\Python\Lib\site-packages') ## adding directory
import pandas as pd
from copy import deepcopy
import numpy as np
from m0_import_pp import pp_choice
from m1_Class_Plants import pp_list,CRF#,biomass

from slices import slice_hrs,demand_64,solar_level,wind_level
from m3_1_availability import fun_availability
from m3_2_dispatch_order import fun_rank_dispatch
from m4_demand_supply import fun_demand_supply
from m5_utilization import fun_pp_utilization 

r = 0.08

##making investment
##----------------decision-making------------------------------------##
#def fun_investment_decision (company_pp_input,year): ##total time steps.


#columns_9 = ['name','plant_type','capacity','running_cost','investment_cost','total_lifetime','lifetime_remain','emission_intensity','profit_index']
def fun_decision_making(ts,rounds,df_pp,carbon_tax):
    print('--------investment process.------------')    
    # ~ candidate_pp = pd.DataFrame(columns = ['name','plant_type','capacity','running_cost','investment_cost','total_lifetime','lifetime_remain','emission_intensity','profit_index'])
    candidate_pp = {'CN_baseload':0,'coal':0,'gas':0,'solar':0,'wind':0} ## set NPV default value as 0.
   
        
    for new_pp in pp_choice.values():##investgate each type of plant.
        
        acc_profit_year = 0
        # =============================================================================
        ##set up new df for new pp.
#        name_new = str(pp_new.plant_type) +'_t'+str(ts) +'_r'+ str(rounds)##name the plant (unique).
#        type_new = pp_new.plant_type
#        capacity_new = pp_new.capacity
#        running_cost_new = pp_new.running_cost
#        investment_cost_new = pp_new.investment_cost
#        tot_life_new = pp_new.lifetime
#         
#        life_remain_new = pp_new.lifetime
#        emission_new = pp_new.emission_intensity
#        marginal_cost_new = pp_new.running_cost + carbon_tax * pp_new.emission_intensity
        
#        new_pp_params = [name_new,pp_new.plant_type,pp_new.capacity,pp_new.running_cost,pp_new.investment_cost,
#                            pp_new.lifetime,pp_new.lifetime,pp_new.emission_intensity,marginal_cost_new]
        
        new_pp['marginal_cost'] = new_pp.running_cost + carbon_tax * new_pp.emission_intensity
        # ~ if new_pp.plant_type.item() == 'gas' and  new_pp.marginal_cost.item()> biomass.running_cost: ## replace natural gas with biogas.
            # ~ new_pp['marginal_cost'] = biomass.running_cost
            
        
#        new_pp = pd.DataFrame([new_pp_params],columns=df_pp.columns)
        
        ##copy the current energy system df.
        df_pp_new = deepcopy(df_pp)
        ##append new pp to df.
#        df_pp_new = df_pp_new.append(new_pp,ignore_index=True,sort=True)## append new pp to df.
        
        # ~ print(df_pp_new[['plant_type','lifetime_remain']])
        
    #    print(system_pp_new)
        df_pp_grouped = df_pp_new.groupby('plant_type',as_index=False).agg({'capacity':'sum','marginal_cost':'mean','emission_intensity':'mean'})
        
        mask = df_pp_grouped.plant_type == new_pp.plant_type.item()##condition.
        ## add capacity of the new_pp to existing df.
        df_pp_grouped.loc[mask, 'capacity'] += new_pp.capacity.item()
        
        # ~ if df_pp_grouped.loc[df_pp_grouped.plant_type == 'gas'].marginal_cost.values>biomass.running_cost: ##if marginal cost of natural gas(default) is bigger than biomass.
            # ~ index_gas = df_pp_grouped.loc[df_pp_grouped.plant_type == 'gas'].index
            # ~ df_pp_grouped.at[index_gas, 'marginal_cost'] = biomass.running_cost## switch to biomass.
                
    # =============================================================================
        ##calculate for each time slice:
        
        for slice_nr in range(64): ##length is 4, loop through.
            demand_level = demand_64[slice_nr]
            avail_solar = solar_level[slice_nr]                    
            avail_wind = wind_level[slice_nr]
            allocated_hours = slice_hrs[slice_nr] ##  hours in current slice.
            # =======================================================
#           print('\n' +'-----new slice: '+ str(allocated_hours) + '(hours)----- ')
#           print('\n' +'-----the slice is: '+ str(time_slice))
#                      
#           print('the demand reference q0 is: ' + str(demand_level))
#           print('The availability of solar is : ' + str (avail_solar))
#           print('The availability of wind is : ' + str (avail_wind))                    
        # =========================================================
                                      
#                    t1_start = time.perf_counter()
#                    print(df_pp_new[['plant_type','capacity']])
            df_pp_grouped['capacity_available_KW'] = df_pp_grouped.apply(lambda row: 
            fun_availability(row.plant_type,avail_solar,avail_wind), axis=1) * df_pp_grouped.capacity
            # ~ availability_index = [1,1,1,avail_solar,avail_wind] ##CN,coal,gas,solar,wind.
            # ~ print(df_pp_grouped)
            # ~ df_pp_grouped['capacity_available_KW'] = df_pp_grouped.capacity * availability_index
            
            new_pp['capacity_available_KW'] = fun_availability(new_pp.plant_type.item(),avail_solar,avail_wind)* new_pp.capacity.item()
                    
            ranked_dispatch = fun_rank_dispatch(df_pp_grouped)
            eq_production,eq_price,last_supply_type,last_supply_percent = fun_demand_supply(df_pp_grouped,ranked_dispatch,demand_level)
            
            new_pp['utilization'] = fun_pp_utilization(new_pp.marginal_cost.item(),last_supply_percent,eq_price)
                    
                    
            #dispatched_KW = pp_utilization * capacit_avail
            new_pp['dispatched_KW'] = new_pp.utilization * new_pp.capacity_available_KW 

            new_pp['hr_profit'] = new_pp.dispatched_KW  * (eq_price - new_pp.marginal_cost.item())
            new_pp['slice_profit'] = new_pp['hr_profit'] * allocated_hours  
                    
            if new_pp.plant_type.item() == 'solar' and avail_solar == 0: ##in this case, solar is not in the df.
                new_plant_slice_profit = 0
            #else:
                #new_plant_slice_profit = new_pp['slice_profit']
                #print('***//////')
                #print(new_plant_slice_profit)
   
            acc_profit_year += new_pp['slice_profit'].item() ##accumulate profit from all time-slices.
                    
            
            # =============================================================================
                    
            # ~ print('\n' + 'The slice_profit_new_plant is : ' + str (new_plant_slice_profit))
            continue
                
                
        #df_pp_grouped['capacity'].loc[df_pp_grouped.plant_type==type_new]-= capacity_new
        ##NPV: geometric sequence summation.    
        NPV_profit = acc_profit_year * (1-(1-r)**new_pp.total_lifetime.item()) / r - new_pp.investment_cost.item() * new_pp.capacity.item() ##NPV minus investment_cost
        # ~ print('the acc_profit_year of this new ' + str(new_pp.plant_type.item())+ ' is ' + str(NPV_profit))
        if NPV_profit > 0:
            CRF_pp = CRF[new_pp.plant_type.item()]
            profit_index = CRF_pp* NPV_profit / (new_pp.investment_cost.item() * new_pp.capacity.item())
            # ~ print('the profit_index of this new ' + str(new_pp.plant_type.item())+ ' is ' + str(profit_index))
        
            # ~ new_pp['profit_index'] = profit_index## define profit index.
            
            # ~ candidate_pp = candidate_pp.append(new_pp,sort=False) ##time= 0.001
            candidate_pp[new_pp.plant_type.item()] = profit_index
            #print('the NPV_profit and profit_index of this new ' + str(name_new)+ ' plant are ')
            #print(NPV_profit,profit_index)
            
#        else:
#            print('It is not profitable to invest in ' + str(name_new)+ ' plant.')
    # =============================================================================
    top_pp = max(candidate_pp, key=lambda key: candidate_pp[key]) ##return the key with highest value(NPV).
    if candidate_pp[top_pp] == 0:
        invest_made = None
    else:
        invest_made = pp_choice[top_pp]
    # ~ if candidate_pp.empty == False:
        
        
        # ~ candidate_pp.sort_values(by=['profit_index'], axis=0, ascending=False, inplace=True)  ## rank candidates by NPV profit.
        # ~ candidate_pp.reset_index(drop=True,inplace=True)
        
        # ~ invest_made = candidate_pp.iloc[0][['name','plant_type','capacity',
        # ~ 'running_cost','investment_cost','total_lifetime','lifetime_remain','emission_intensity']]## select the first row-plant with the highest profit index.
# ~ #        print(invest_made)
        
        
    # ~ else:
        # ~ invest_made = None
#   print('One ' + str(invest_made) + ' is invested by ' + ' company ' + '.')
     
#            
    return invest_made










