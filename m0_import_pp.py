#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
import initial company's power plant portfolio.

"""
import sys
sys.path.append('C:\PhD_Chalmers\Python\Lib\site-packages') ## adding directory
import pandas as pd
#pd.set_option('display.max_columns', 12)

comp0_initial_PP = pd.read_excel("input/company_initial_profile.xlsx",sheet_name="input_initial_500",header=1) 

df_invest_choice = pd.read_excel("input/company_initial_profile.xlsx",sheet_name="new_pp",header=1,sort=True)

pp_choice = {
'CN_baseload':df_invest_choice[df_invest_choice.plant_type == 'CN_baseload']
,'coal':df_invest_choice[df_invest_choice.plant_type == 'coal']
,'gas':df_invest_choice[df_invest_choice.plant_type == 'gas']
,'solar':df_invest_choice[df_invest_choice.plant_type == 'solar']
,'wind':df_invest_choice[df_invest_choice.plant_type == 'wind']
}


# ~ print(comp0_initial_PP.capacity.sum())
