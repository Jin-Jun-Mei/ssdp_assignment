
import sys
sys.path.append('C:\PhD_Chalmers\Python\Lib\site-packages') ## adding directory
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
today = datetime.date.today()
from m1_Class_Plants import pp_list,fuel_list,biomass
from m2_demand_slices import q0_hr_slice,q0t,availability_levels_solar,availability_levels_wind
from m2_slices import slice_hrs
from m3_1_availability import fun_availability
from m3_2_dispatch_order import fun_rank_dispatch
from m4_demand_supply import fun_demand_supply
from m5_utilization import fun_pp_utilization
from m7_plot_dispatch_slice import func_plot_dispatch_slice
from m7_plot_dispatch_yr import func_plot_dispatch_yr
from m10_switch_bio import func_switch_bio
from m11_func_switch_type import func_switch_type
pd.set_option('display.max_columns', 12)
pd.options.mode.chained_assignment = None
import pdb

# ~ pdb.set_trace() ##set breakpoint

# =============================================================================
##1.1import data: installed_capacity.
file_path1 = "output/tables/installed/"
file_name1 = "installed_capacity_2019-06-17.xlsx"
# ~ file_comp0 = "yr_installed_comp0_heter_2019-05-30.xlsx"
# ~ file_comp1 = "yr_installed_comp1_heter_2019-05-30.xlsx"
# ~ file_comp2 = "yr_installed_comp2_heter_2019-05-30.xlsx"

df_installed = pd.read_excel(file_path1+file_name1,header=0,index_col=0)
df_installed.fillna(value=0,inplace=True)##fill the NaN vaulue with 0.
# ~ print(df_installed)
n =len(df_installed.columns)#length of columns.
df_installed.set_axis(np.array(['capacity']*n), axis='columns', inplace=True) ##rename column name to 'capacity'.

##on individual agent level.
# ~ comp0_installed = pd.read_excel(file_path1+file_comp0,header=0,index_col=0)
# ~ comp1_installed = pd.read_excel(file_path1+file_comp1,header=0,index_col=0)
# ~ comp2_installed = pd.read_excel(file_path1+file_comp2,header=0,index_col=0)

# ~ comp0_installed.fillna(value=0,inplace=True)
# ~ comp1_installed.fillna(value=0,inplace=True)
# ~ comp2_installed.fillna(value=0,inplace=True)

# ~ comp0_installed.set_axis(np.array(['capacity']*n), axis='columns', inplace=True) ##rename column name to 'capacity'.
# ~ comp1_installed.set_axis(np.array(['capacity']*n), axis='columns', inplace=True) ##rename column name to 'capacity'.
# ~ comp2_installed.set_axis(np.array(['capacity']*n), axis='columns', inplace=True) ##rename column name to 'capacity'.
# =============================================================================

##1.2.concating attributes (running cost, emission intensity)##
df_attribute = pd.DataFrame({'running_cost': [pp.running_cost for pp in pp_list], 
'emission_intensity': [pp.emission_intensity for pp in pp_list]},index=[pp.plant_type for pp in pp_list])
df_pp_pi = pd.concat([df_attribute,df_installed], axis=1, sort=True, copy=False )##concat two df.
# ~ comp0_installed = pd.concat([df_attribute,comp0_installed], axis=1, sort=True, copy=False )##concat two df.
# ~ comp1_installed = pd.concat([df_attribute,comp1_installed], axis=1, sort=True, copy=False )##concat two df.
# ~ comp2_installed = pd.concat([df_attribute,comp2_installed], axis=1, sort=True, copy=False )##concat two df.

df_pp_pi.reset_index(level=0, inplace=True)## reset index
# ~ comp0_installed.reset_index(level=0, inplace=True)## reset index
# ~ comp1_installed.reset_index(level=0, inplace=True)## reset index
# ~ comp2_installed.reset_index(level=0, inplace=True)## reset index

df_pp_pi.rename({'index':'plant_type'}, axis='columns',inplace=True) ##rename column.
# ~ comp0_installed.rename({'index':'plant_type'}, axis='columns',inplace=True) ##rename column.
# ~ comp1_installed.rename({'index':'plant_type'}, axis='columns',inplace=True) ##rename column.
# ~ comp2_installed.rename({'index':'plant_type'}, axis='columns',inplace=True) ##rename column.
# ~ print(df_pp_pi)

# =============================================================================
##1.3 set-up empty df for plottings.
yr_dispatched_series = pd.DataFrame(index=[pp.plant_type for pp in fuel_list])
slice_dispatched_series = pd.DataFrame(index=[pp.plant_type for pp in fuel_list])
# ~ pdb.set_trace() ##set breakpoint

##1.4 set-up list for plottings.
sliced_hours = np.reshape(q0_hr_slice, 64, order='C')
annual_price_average1 = np.array([]) ## for recording average electricity price of each year. ##average by production.

##1.5 set-up empty df for recording results(profit)
yr_revenue_series = pd.DataFrame(index=[pp.plant_type for pp in pp_list])
#system level
yr_operate_profit_series = pd.DataFrame(index=[pp.plant_type for pp in pp_list])
##individual agent level.
# ~ yr_operate_profit_comp0_series = pd.DataFrame(index=[pp.plant_type for pp in pp_list])
# ~ yr_operate_profit_comp1_series = pd.DataFrame(index=[pp.plant_type for pp in pp_list])
# ~ yr_operate_profit_comp2_series = pd.DataFrame(index=[pp.plant_type for pp in pp_list])



# ============================================================================
##2.calculating el. price, dispatch, revenue and ect.
for year in range (n):
    print('\n' +'----- year: '+ str(year)+'----- ')
    ##2.1 slicing the column, and select capacity of current year.
    df_pp = df_pp_pi.iloc[:,[0,1,2,year+3]]
    # ~ df_comp0 = comp0_installed.iloc[:,[0,1,2,year+3]]
    # ~ df_comp1 = comp1_installed.iloc[:,[0,1,2,year+3]]
    # ~ df_comp2 = comp2_installed.iloc[:,[0,1,2,year+3]]
    # ===================================================================
    # 2.2 set carbon_tax
    if year <= 10:
        carbon_tax = 0  ## carbon tax is 0 before year 10.
    elif 10 <= year <= 50:
        carbon_tax = 250 * year - 2500 ## from year 10 to 50, carbon tax increases linearly to 10000 cent/ton.
    else:
        carbon_tax = 10000   ## after year 50, carbon tax stays at 10000 cent/ton.
    # =================================================================
    
    # creat empty lists and initial values.
    eq_price_slice_64 = np.array([])
    dispatched_slice_64 = np.array([])
    coal_dispatch_slice = np.array([])
    
    slice_nr = 0
    df_pp['dispatched_yr'] = 0
    df_pp['revenue_yr'] = 0
    df_pp['operate_profit_yr'] = 0 
    # ~ df_comp0 ['operate_profit_yr'] = 0 
    # ~ df_comp1 ['operate_profit_yr'] = 0 
    # ~ df_comp2 ['operate_profit_yr'] = 0 
    
    df_pp['marginal_cost'] = df_pp['running_cost'] + carbon_tax * df_pp['emission_intensity']
    # ~ df_comp0['marginal_cost'] = df_comp0['running_cost'] + carbon_tax * df_comp0['emission_intensity']
    # ~ df_comp1['marginal_cost'] = df_comp0['running_cost'] + carbon_tax * df_comp1['emission_intensity']
    # ~ df_comp2['marginal_cost'] = df_comp0['running_cost'] + carbon_tax * df_comp2['emission_intensity']
    
    if biomass in fuel_list: ##check whether biofuel is available.
        ##if natural gas is more expensive than biogas.
        df_pp = func_switch_bio(df_pp,biomass.running_cost)
        # ~ df_comp0 = func_switch_bio(df_comp0,biomass.running_cost)
        # ~ df_comp1 = func_switch_bio(df_comp1,biomass.running_cost)
        # ~ df_comp2 = func_switch_bio(df_comp2,biomass.running_cost)
            
            
            # ~ print('yes, biomass.')
    # ===============================================================
    ##start ex-post analysis.
    for q0 in range(len(q0t)): ##length is 4, loop through.
        demand_level = q0t[q0]
        for solar_index in range(len(availability_levels_solar)):##4 levels of solar availability.
            avail_solar = availability_levels_solar[solar_index]
            for wind_index in range(len(availability_levels_wind)):
                avail_wind = availability_levels_wind[wind_index]
                allocated_hours = q0_hr_slice[q0][solar_index][wind_index] ##  hours in current slice.
                # =======================================================
                df_pp['capacity_available_KW'] = df_pp.apply(lambda row: fun_availability(row.plant_type,avail_solar,avail_wind),axis=1) * df_pp.capacity
                # ~ df_comp0['capacity_available_KW'] = df_comp0.apply(lambda row: fun_availability(row.plant_type,avail_solar,avail_wind),axis=1) * df_comp0.capacity
                # ~ df_comp1['capacity_available_KW'] = df_comp1.apply(lambda row: fun_availability(row.plant_type,avail_solar,avail_wind),axis=1) * df_comp1.capacity
                # ~ df_comp2['capacity_available_KW'] = df_comp2.apply(lambda row: fun_availability(row.plant_type,avail_solar,avail_wind),axis=1) * df_comp2.capacity
                
                ranked_dispatch = fun_rank_dispatch(df_pp)
                
                eq_production,eq_price,last_supply_type,last_supply_percent = fun_demand_supply(df_pp,ranked_dispatch,demand_level)
                
                eq_price_slice_64 = np.append(eq_price_slice_64,[eq_price])
            
                df_pp['utilization'] = df_pp.apply(lambda row: fun_pp_utilization(row.marginal_cost,last_supply_percent,eq_price),axis=1)
                # ~ df_comp0['utilization'] = df_comp0.apply(lambda row: fun_pp_utilization(row.marginal_cost,last_supply_percent,eq_price),axis=1)
                # ~ df_comp1['utilization'] = df_comp1.apply(lambda row: fun_pp_utilization(row.marginal_cost,last_supply_percent,eq_price),axis=1)
                # ~ df_comp2['utilization'] = df_comp2.apply(lambda row: fun_pp_utilization(row.marginal_cost,last_supply_percent,eq_price),axis=1)
                
                
                
                df_pp['slice_dispatched_KWH'] = df_pp.utilization * df_pp.capacity_available_KW ##one slice, multiplied with allocated_hours
                
                df_pp['slice_dispatched_KWHs'] = df_pp.slice_dispatched_KWH *allocated_hours ##one slice, multiplied with allocated_hours
                
                # ~ df_comp0['slice_dispatched_KWHs'] = df_comp0.utilization * df_comp0.capacity_available_KW *allocated_hours ##one slice, multiplied with allocated_hours
                # ~ df_comp1['slice_dispatched_KWHs'] = df_comp1.utilization * df_comp1.capacity_available_KW *allocated_hours ##one slice, multiplied with allocated_hours
                # ~ df_comp2['slice_dispatched_KWHs'] = df_comp2.utilization * df_comp2.capacity_available_KW *allocated_hours ##one slice, multiplied with allocated_hours
                
                df_pp['revenue_slice'] = df_pp.slice_dispatched_KWHs * eq_price
                df_pp['operating_cost_slice'] = df_pp.slice_dispatched_KWHs * df_pp.marginal_cost
                
                df_pp['operate_profit_slice'] = df_pp.revenue_slice - df_pp.operating_cost_slice
                # ~ df_comp0['operate_profit_slice'] = df_comp0.slice_dispatched_KWHs * (eq_price - df_comp0.marginal_cost)
                # ~ df_comp1['operate_profit_slice'] = df_comp1.slice_dispatched_KWHs * (eq_price - df_comp1.marginal_cost)
                # ~ df_comp2['operate_profit_slice'] = df_comp2.slice_dispatched_KWHs * (eq_price - df_comp2.marginal_cost)
                
                # ======================================================
                
                # ======================================================
                ##recording slice results.
                ##1. dispatch of each slice.
                slice_dispatch =  df_pp[['plant_type','slice_dispatched_KWH']].set_index('plant_type')
                slice_dispatched_series[str(slice_nr)] = pd.concat([slice_dispatch], axis=1, sort=True)
                
                ##2. sum-up production from all types of pp, for calcuating average price.
                dispatched_slice_64 = np.append(dispatched_slice_64,[df_pp['slice_dispatched_KWHs'].sum()]) 
                
                ##3. accumulate slice results.
                df_pp['dispatched_yr'] += df_pp.slice_dispatched_KWHs
                df_pp['revenue_yr'] += df_pp.revenue_slice
                df_pp['operate_profit_yr'] += df_pp.operate_profit_slice
                # ~ df_comp0['operate_profit_yr'] += df_comp0.operate_profit_slice
                # ~ df_comp1['operate_profit_yr'] += df_comp1.operate_profit_slice
                # ~ df_comp2['operate_profit_yr'] += df_comp2.operate_profit_slice
                # ~ print(df_pp['slice_dispatched_KWHs'])
                # ~ print(dispatched_slice_64)          
                slice_nr +=1
                
                continue
            continue    
        continue
    
    # =========================================================================# 
    ##record yearly results.
    #dispatch
    yr_dispatch =  df_pp[['plant_type','dispatched_yr']].set_index('plant_type')
    yr_dispatched_series[str(year)] = pd.concat([yr_dispatch], axis=1, sort=True)
    
    #revenue & profit
    df_pp = func_switch_type(df_pp,'biomass','gas') 
    # ~ df_comp0 = func_switch_type(df_comp0,'biomass','gas')
    # ~ df_comp1 = func_switch_type(df_comp1,'biomass','gas')
    # ~ df_comp2 = func_switch_type(df_comp2,'biomass','gas')
    # ~ index_biomass = df_pp.loc[df_pp.plant_type == 'biomass'].index
    # ~ df_pp.at[index_biomass, 'plant_type'] = 'gas' ## switch name of biomass to gas.
    
    ##system level
    yr_revenue =  df_pp[['plant_type','revenue_yr']].set_index('plant_type')
    yr_revenue_series[str(year)] = pd.concat([yr_revenue], axis=1, sort=True)
    
    yr_operate_profit = df_pp[['plant_type','operate_profit_yr']].set_index('plant_type')##select 2 columns.
    yr_operate_profit_series[str(year)] = pd.concat([yr_operate_profit], axis=1, sort=True)
    
    # ~ ##comp0
    # ~ yr_operate_profit = df_comp0[['plant_type','operate_profit_yr']].set_index('plant_type')##select 2 columns.
    # ~ yr_operate_profit_comp0_series[str(year)] = pd.concat([yr_operate_profit], axis=1, sort=True)
    # ~ ##comp1
    # ~ yr_operate_profit = df_comp1[['plant_type','operate_profit_yr']].set_index('plant_type')##select 2 columns.
    # ~ yr_operate_profit_comp1_series[str(year)] = pd.concat([yr_operate_profit], axis=1, sort=True)
    # ~ ##comp2
    # ~ yr_operate_profit = df_comp2[['plant_type','operate_profit_yr']].set_index('plant_type')##select 2 columns.
    # ~ yr_operate_profit_comp2_series[str(year)] = pd.concat([yr_operate_profit], axis=1, sort=True)
        
    
    ##calculate annual averaged price.
    annual_price_average1 = np.append(annual_price_average1,[(eq_price_slice_64*dispatched_slice_64).sum()/dispatched_slice_64.sum()]) ## total revenue divided by total production.
     # ~ print(yr_operate_profit)
   
    # =========================================================================# 
    ##ploting results.
    
    #plot all production slices in a year. 
    # ~ slice_dispatched_series.fillna(value=0,inplace=True)
    # ~ func_plot_dispatch_slice(slice_dispatched_series,eq_price_slice_64,title='electricity dispach in slices(KW) in year '+ str(year),yr=year)
    
    
    # ================print slice electricity price ============# 
    # ~ np.savetxt("output/tables/slice_price_dispatch/el_price\year_" + str(year)+'_r'+str(biomass.running_cost)+".txt", eq_price_slice_64, delimiter=',', fmt='%1.3f') 

    # ~ sorted_eq_price,sorted_dispatched = zip(*sorted(zip(np.round_(eq_price_slice_64, decimals=1),dispatched_slice_64)))  
    # ~ sorted_dispatched = np.asarray(sorted_dispatched)/dispatched_slice_64.sum()##normalization.
    # ~ xbins = np.cumsum(sorted_dispatched)##Return the cumulative sum of the elements along a given axis.
    # ~ fig = plt.figure(figsize=(16,9))
    # ~ plt.step(xbins, sorted_eq_price, linewidth=2.5, color="k",where="mid")
    # ~ tick=0
    # ~ for x, y in zip(xbins, sorted_eq_price):
        # ~ if sorted_eq_price[tick] != sorted_eq_price[tick-1] :#and xbins[tick]-xbins[tick-1]>0.001:
            # ~ plt.text(x, y*1.1, str(y), color="red", fontsize=10)
        # ~ tick +=1    
    # ~ plt.yscale('symlog') ##symmetric log scale.
    # ~ plt.title('electricity price in year '+ str(year), fontsize=16)
    # ~ plt.xlabel('% of total annual production')
    # ~ plt.ylabel('euro cent / KWh')
    # ~ plt.savefig("output/figures/el_price/slice_price_r6_i9\yr" + str(year), dpi=600)
    # ~ if year > 60:
        # ~ plt.show()
    # ~ plt.clf()
    
    continue


# ~ print(yr_dispatched_series)
# ~ print(yr_operate_profit_series)
# ~ print(annual_price_average)
# =========================plotting===============================# 
##plot yearly average electricity price

plt.plot(annual_price_average1,color='turquoise',label='heter agents')
plt.title('annual average electricity price', fontsize=16)
plt.xlabel('year', fontsize=14)
plt.ylabel('euro cent / KWh', fontsize=14)
plt.ylim(3,max(annual_price_average1)+0.5)
plt.grid(True)
plt.legend()
plt.show()

##plot dispatched electricity.
yr_dispatched_series.fillna(value=0,inplace=True)
func_plot_dispatch_yr(yr_dispatched_series,title='electricity dispached (KWh)',yr=year)
# ~ plt.savefig("output/figures/dispath/"+ str(today)+".png", dpi=600)

# ===========================================================# 
##export the results.
file_path2 = "output/tables/dispatched/"
file_path3 = "output/tables/profit/"
file_path4 = "output/tables/el_price/"

file_name_dispatch = "dispatch_CRF_"+ str(today)+".xlsx"
file_name_revenue = "revenue_CRF_"+ str(today)+".xlsx"
file_name_profit = "profit_CRF_"+ str(today)+".xlsx"
file_name_el_price = "el_price_CRF_"+ str(today)+".xlsx"

yr_dispatched_series.to_excel(file_path2 + file_name_dispatch)     
yr_revenue_series.to_excel(file_path3 + file_name_revenue )     
yr_operate_profit_series.to_excel(file_path3 +file_name_profit )     
df_aver_price = pd.DataFrame (annual_price_average1)
df_aver_price.to_excel(file_path4 + file_name_el_price)   



# ~ ##agent level
# ~ yr_operate_profit_comp0_series.to_excel(file_path3 + 'comp0_'+ file_name_profit )
# ~ yr_operate_profit_comp1_series.to_excel(file_path3 + 'comp1_'+ file_name_profit )  
# ~ yr_operate_profit_comp2_series.to_excel(file_path3 + 'comp2_'+ file_name_profit )   
# ~ func_plot_dispatch_yr(yr_operate_profit_comp0_series,title='yr_operate_profit_comp0_series',yr=year)
