#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
demand_supply module.
calculate equilibrium prduction and price in each hour.

@author: jinxi
"""
 
def fun_demand_supply(df_sys_pp,ranked_dispatch,demand_level):
    
    #marginal_costs = ranked_dispatch['marginal_cost'] ## comment it out to avoid coping.
    #generation_capacities = ranked_dispatch['capacity_available_KW']
    #print('ranked_dispatch is //////////')
    #print(ranked_dispatch)
    eps = -0.05
    p0 = 3
    q0 = demand_level
    
# =============================================================================
    for index,row in ranked_dispatch.iterrows():
        q_demand = sum(ranked_dispatch['capacity_available_KW'][0:index+1])
#        print(generation_capacities)
        demand_price = p0 * q0 ** (-1 / eps) * q_demand ** (1 / eps)
        if demand_price <= ranked_dispatch['marginal_cost'][index]:
            #print('in 1')
            eq_price = ranked_dispatch['marginal_cost'][index]## means price will be the running cost of first type.
            eq_production = q0 * (eq_price / p0) ** eps 
            break
        else: ##if demand_price > run_costs[i]
            eq_production =  q_demand
            eq_price = demand_price
            if sum(ranked_dispatch['capacity_available_KW'][:]) - sum(ranked_dispatch['capacity_available_KW'][0:index+1]) > 0 and \
            demand_price > ranked_dispatch['marginal_cost'][index+1]: ## first if :## if there is still remaining/unruned production/plants.second if: check if on the vertical line
                #generated_pp[generation_type[i]] = generation_capacities[i] ##but without the last supply.
                continue
                   
            else: ## if demand_price <= run_costs[i+1]
                break
    
    last_dispatch_type = ranked_dispatch.at[index,'plant_type']  ##get the name of the last supply plant type.
    #print('\n' + 'The last_dispatch_type is: ' + str(last_dispatch_type)  )
            
    other_dispatch_amount = ranked_dispatch['capacity_available_KW'].iloc[0:index].sum()
    
    
    last_tp_dispatch_amount = eq_production - other_dispatch_amount
    last_dispatch_available = ranked_dispatch[ranked_dispatch.plant_type== last_dispatch_type]['capacity_available_KW'].values[0]
    #print('And last_dispatch_available: ' + str(last_dispatch_available))
    #last_supply_nr = df_sys_pp['plant_type'][df_sys_pp.plant_type == last_dispatch_type].count()
    #print('And the last_supply_nr: ' + str(last_supply_nr))
    
    last_supply_percent = last_tp_dispatch_amount / last_dispatch_available
    
    
    #print('\n' + 'The total dispatched electricity is: ' + str(eq_production) +'KW.'  )
    #print('And the eq price is: ' + str(eq_price)+ ' cent/kwh.')
    #print('The last dispatch type is: ' + str(last_dispatch_type))
       
    
    return eq_production,eq_price,last_dispatch_type,last_supply_percent
    
    
    
    
    



















