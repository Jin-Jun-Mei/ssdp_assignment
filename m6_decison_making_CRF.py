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
import pdb ##debugging
import numpy as np
from m0_import_pp import pp_choice
from m1_Class_Plants import pp_list,fuel_list,biomass
from m2_slices import slice_hrs,demand_64,solar_level,wind_level
from m3_1_availability import fun_availability
from m3_2_dispatch_order import fun_rank_dispatch
from m4_demand_supply import fun_demand_supply
from m5_utilization import fun_pp_utilization 

##making investment
##----------------decision-making------------------------------------##
#def fun_investment_decision (company_pp_input,year): ##total time steps.
print('--------Start investment process.------------')

#columns_9 = ['name','plant_type','capacity','running_cost','investment_cost','total_lifetime','lifetime_remain','emission_intensity','profit_index']
def fun_decision_making(df_pp,carbon_tax,r):
    
    # ~ candidate_pp = pd.DataFrame(columns = ['name','plant_type','capacity','running_cost','investment_cost','total_lifetime','lifetime_remain','emission_intensity','profit_index'])
    candidate_pp = {'CN_baseload':0,'coal':0,'gas':0,'solar':0,'wind':0} ## set NPV default value as 0.
   
        
    for pp in pp_choice.values():##investgate each type of plant.
        new_pp = deepcopy(pp)##set up new df for new pp.
        new_pp['marginal_cost'] = new_pp.running_cost + carbon_tax * new_pp.emission_intensity
        # =============================================================================
        
        ##copy the current supply system df.
        df_pp_new = deepcopy(df_pp)        
        ##group the pp by plant type.
        df_pp_grouped = df_pp_new.groupby('plant_type',as_index=False).agg({'capacity':'sum','marginal_cost':'mean','emission_intensity':'mean'})
        
        mask = df_pp_grouped.plant_type == new_pp.plant_type.item()##condition.
        ## add capacity of the new_pp to existing df.
        df_pp_grouped.loc[mask, 'capacity'] += new_pp.capacity.item()
        
        # ============================================================================= 
        ##check whether biofuel is available.
        if biomass in fuel_list:
            if df_pp_grouped.loc[df_pp_grouped.plant_type == 'gas'].marginal_cost.values>biomass.running_cost: ##if marginal cost of natural gas(default) is bigger than biomass.
                index_gas = df_pp_grouped.loc[df_pp_grouped.plant_type == 'gas'].index
                df_pp_grouped.at[index_gas, 'marginal_cost'] = biomass.running_cost## switch to biomass.
            
            if new_pp.plant_type.item() == 'gas' and  new_pp.marginal_cost.item()> biomass.running_cost: ## replace natural gas with biogas
                new_pp['marginal_cost'] = biomass.running_cost
        # =============================================================================
        ##calculate for each time slice:
        acc_profit_year = 0 ##accumulative profit.
        
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
#            df_pp_grouped['capacity_available_KW'] = df_pp_grouped.apply(lambda row: 
#            fun_availability(row.plant_type,avail_solar,avail_wind), axis=1) * df_pp_grouped.capacity
            availability_index = [1,1,1,avail_solar,avail_wind] ##CN,coal,gas,solar,wind.
            
            df_pp_grouped['capacity_available_KW'] = df_pp_grouped.capacity * availability_index
            
            new_pp['capacity_available_KW'] = fun_availability(new_pp.plant_type.item(),avail_solar,avail_wind)* new_pp.capacity.item()
                    
            ranked_dispatch = fun_rank_dispatch(df_pp_grouped)
            eq_production,eq_price,last_supply_type,last_supply_percent = fun_demand_supply(df_pp_grouped,ranked_dispatch,demand_level)
            
            new_pp['utilization'] = fun_pp_utilization(new_pp.marginal_cost.item(),last_supply_percent,eq_price)
                    
                    
            ##dispatched_KW = pp_utilization * capacity_avail
            new_pp['dispatched_KW'] = new_pp.utilization * new_pp.capacity_available_KW 

            new_pp['hr_profit'] = new_pp.dispatched_KW  * (eq_price - new_pp.marginal_cost.item())
            new_pp['slice_profit'] = new_pp['hr_profit'] * allocated_hours  
                    
            # ~ if new_pp.plant_type.item() == 'solar' and avail_solar == 0: ##in this case, solar is not in the df.
                # ~ new_plant_slice_profit = 0
            #else:
                #new_plant_slice_profit = new_pp['slice_profit']
                #print('***//////')
                #print(new_plant_slice_profit)
   
            acc_profit_year += new_pp['slice_profit'].item() ##accumulate profit from all time-slices.
            # ~ print('\n' + 'The slice_profit_new_plant is : ' + str (new_plant.slice_profit))
            continue
            
        # =============================================================================
        ##calculate NPV: geometric sequence summation.    
        NPV_profit = acc_profit_year * (1-(1-r)**new_pp.total_lifetime.item()) / r - new_pp.investment_cost.item() * new_pp.capacity.item() ##NPV minus investment_cost
        # ~ print('the acc_profit_year of this new ' + str(new_pp.plant_type.item())+ ' is ' + str(NPV_profit))
        if NPV_profit > 0:
            lifetime = new_pp.total_lifetime.item()
            CRF_pp = r*(1+r)**lifetime/((1+r)**lifetime-1)
            # ~ print(CRF_pp)
            profit_index = CRF_pp* NPV_profit / (new_pp.investment_cost.item() * new_pp.capacity.item())
            # ~ print('the profit_index of this new ' + str(new_pp.plant_type.item())+ ' is ' + str(profit_index))
            # ~ pdb.set_trace()
            
            # ~ candidate_pp = candidate_pp.append(new_pp,sort=False) ##time= 0.001
            candidate_pp[new_pp.plant_type.item()] = profit_index
            #print('the NPV_profit and profit_index of this new ' + str(name_new)+ ' plant are ')
            #print(NPV_profit,profit_index)
            
#        else:
#            print('It is not profitable to invest in ' + str(name_new)+ ' plant.')
    # =============================================================================
    top_pp = max(candidate_pp, key=lambda key: candidate_pp[key]) ##return the key with highest value(NPV).
    if candidate_pp[top_pp] == 0: ##NPV is zero.
        invest_made = None
    else:
        invest_made = pp_choice[top_pp]
                
    return invest_made










