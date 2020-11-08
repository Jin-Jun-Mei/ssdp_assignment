import sys
sys.path.append('C:\PhD_Chalmers\Python\Lib\site-packages') ## adding directory
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from m1_Class_Plants import pp_list
from m2_demand_slices import q0_hr_slice,q0t,availability_levels_solar,availability_levels_wind
from m3_1_availability import fun_availability
from m3_2_dispatch_order import fun_rank_dispatch
from m4_demand_supply import fun_demand_supply
from m5_utilization import fun_pp_utilization
from m7_plot_install import func_plot_install
pd.set_option('display.max_columns', 12)
pd.options.mode.chained_assignment = None

import pdb
# ~ pdb.set_trace() ##set breakpoint

# ====================================================================
##import data     
file_path = "output/tables/"
#case 1 : homogeneous+no bio.
# ~ file_name_revenue1 = "profit/revenue_homo_obio_2019-05-15.xlsx"
# ~ file_name_operate_profit1 = "profit/operate_profit_homo_obio_2019-05-15.xlsx"
# ~ file_name_installed1 = "installed/installed_capacity_homo_obio2019-05-15.xlsx "
# ~ file_name_investNr1 = "installed/pp_invest_nr_homo_obio2019-05-15.xlsx"

# ~ df_revenue1 = pd.read_excel(file_path + file_name_revenue1,header=0,index_col=0) ## 70 years.
# ~ df_operate_profit1 = pd.read_excel(file_path + file_name_operate_profit1,header=0,index_col=0) 
# ~ df_installed1 = pd.read_excel(file_path + file_name_installed1,header=0,index_col=0)
# ~ df_invest_nr1 = pd.read_excel(file_path + file_name_investNr1,header=0) 
# ========================================================================
#case 2 : homogeneous+ with bio.
file_name_revenue2 = "profit/revenue_CRF_2019-06-17.xlsx"
file_name_operate_profit2 = "profit/profit_CRF_2019-06-17.xlsx"
file_name_installed2 = "installed/installed_capacity_2019-06-17.xlsx "
file_name_investNr2 = "installed/pp_invest_nr_2019-06-17.xlsx"

df_revenue2 = pd.read_excel(file_path + file_name_revenue2,header=0,index_col=0) ## 70 years.
df_operate_profit2 = pd.read_excel(file_path + file_name_operate_profit2,header=0,index_col=0) 
df_installed2 = pd.read_excel(file_path + file_name_installed2,header=0,index_col=0)
df_invest_nr2 = pd.read_excel(file_path + file_name_investNr2,header=0) 
# ~ df_invest_nr2 = df_invest_nr2[[pp.plant_type for pp in pp_list]] ## rearrange the order of columns to match.
# ~ print(df_invest_nr2)

# ========================================================================
# ========================================================================
##extend the columns to yr 109.
addition_year=list(range(70,110,1))
##list of df that need to be extended.
df_extend_list = [df_revenue2,df_operate_profit2,df_installed2]
for year in addition_year:
    for df_extend in df_extend_list:
        df_extend[year] = df_extend.iloc[:,69] ##add data from year 70 to 109 as the same as yr 69.
##fill in NA value with 0.
# ~ df_revenue2.fillna(value=0,inplace=True) ## fill the NaN value with 0.
# ~ df_operate_profit2.fillna(value=0,inplace=True) ## fill the NaN value with 0.
# ~ df_installed2.fillna(value=0,inplace=True)

# ~ print(df_operate_profit2)


# ======================================================================
# ===================================================================
##set parameters.
n =len(df_invest_nr2.index)#length of the array, which is 70yr.
r =0.08 ##discount rate.
# ~ with open('output\investment_evaluate/investment_results.txt', 'w') as f:  ##write the results to external txt.

## plotting parameters
i= 0  
fig = plt.figure(figsize=(20,15))##set size of the plot.
# ~ ax1 = fig.add_subplot(211)## divide the plot into two rows.
ax2 = fig.add_subplot(111)
color_opt = ['silver','saddlebrown','slateblue','gold','olivedrab']

# ======================================================================
##define a function to calculate the NPV of a investment: profit - investment.
def func_NPV (year,pp_profit,pp_installed_capacity,pp_investment_cost,pp_capacity,pp_lifetime):
    ##geometric series od discount rate.
    discount_series = np.geomspace(1, (1+r)**pp.lifetime, num = pp_lifetime)
    ##convert df to numpy array.
    pp_profit = pp_profit.to_numpy(dtype=None, copy=False)[year+1:year+pp_lifetime+1]
    annual_installed = pp_installed_capacity.to_numpy(dtype=None, copy=False)[year+1:year+pp_lifetime+1]
    ##profit of one single plant.
    op_pf_one = pp_profit / annual_installed * pp_capacity
    
    ##NPV_invest = (sum of profit-investment_cost) / investment_cost
    NPV_invest = ((op_pf_one / discount_series).sum() - pp_investment_cost * pp_capacity)/(pp_investment_cost*pp_capacity)
    print(NPV_invest)
    return NPV_invest
    
# ===================================================================
# ===================================================================
##ex-post analysis of the NPV of each investment.
for pp in pp_list:
    print(pp.plant_type) 
    invest_cost = pp.investment_cost
    capacity = pp.capacity
    lifetime = pp.lifetime
    ##case 1
    # ~ operate_profit1 = df_operate_profit1.loc[pp.plant_type]
    # ~ installed1 = df_installed1.loc[pp.plant_type]
    ##case 2
    operate_profit2 = df_operate_profit2.loc[pp.plant_type]
    installed2 = df_installed2.loc[pp.plant_type]
    
    
    for invest_year in range(n):
        # ~ print(df_invest_nr2[pp.plant_type][invest_year])## number of investment made.
        # ================================================================
        # ~ if df_invest_nr1[pp.plant_type][invest_year] > 0 : ##there was investment made this year.
            # ~ NPV_ivm1 = func_NPV (invest_year,operate_profit1,installed1,invest_cost,capacity,lifetime)
            # ~ ax1.scatter(invest_year, NPV_ivm1, color= color_opt[i],label=pp.plant_type) ##plot a dot.
            # ~ ax1.plot(invest_year, NPV_ivm1,linestyle='--', marker='o', color= color_opt[i],label=pp.plant_type) 
            
            # ~ print('\n'+ 'investment year: '+ str(invest_year))
            # ~ print('the NPV is '+str(func_NPV (invest_year,pp)))
            # ~ print( 'NPV/investment of '+ str(pp.plant_type)+ ' is ' + str(NPV_a))
         
        
        if df_invest_nr2[pp.plant_type][invest_year] > 0 : ##there was investment made this year.
            NPV_ivm2 = func_NPV (invest_year,operate_profit2,installed2,invest_cost,capacity,lifetime)
            # ~ print('npv')
            # ~ print(NPV_ivm2)
            ax2.scatter(invest_year, NPV_ivm2, color= color_opt[i],label=pp.plant_type)    
            # ~ print('\n'+ 'investment year: '+ str(invest_year))
            # ~ print( 'NPV/investment of '+ str(pp.plant_type)+ ' is ' + str(NPV))
          
                
        continue    
    i+=1
    continue            
# ~ print( pp.plant_type + ' investment in year: '+ str(invest_year) + rst  ,file=f)     


# =======================================================
##set ploting parameters.
# ~ ax1.set_title('case one homogeneous agents, no bio: )',fontsize= 16)
ax2.set_title('Ex-post investment analysis 8%(CRF) )',fontsize= 16)
# ~ ax1.set_ylabel('NPV / Investment cost',fontsize= 16)
ax2.set_ylabel('NPV / Investment cost',fontsize= 16)
ax2.set_xlabel('year',fontsize= 12)
# ~ ax1.set_yscale("symlog")##symmetric log scale.
# ~ ax2.set_yscale("symlog")##symmetric log scale.
# ~ ax1.grid(b=True, axis='y')##trun the grid on.
ax2.grid(b=True, axis='y')##trun the grid on.
    

legend_elements = [Line2D([0], [0], marker='o', color=color_opt[0]),
                   Line2D([0], [0], marker='o', color=color_opt[1]),
                   Line2D([0], [0], marker='o', color=color_opt[2]),
                   Line2D([0], [0], marker='o', color=color_opt[3]),
                   Line2D([0], [0], marker='o', color=color_opt[4])]
plt.legend(handles = legend_elements, labels=(pp.plant_type for pp in pp_list))    
# ~ plt.legend((lo, ll, l, a, h, hh, ho),
           # ~ (index=[pp.plant_type for pp in pp_list]),
           # ~ scatterpoints=1,
           # ~ loc='lower left',
           # ~ ncol=3,
           # ~ fontsize=8)
              
    # ~ plt.legend(scatterpoints = 1)

plt.show()
plt.clf()
plt.close()
