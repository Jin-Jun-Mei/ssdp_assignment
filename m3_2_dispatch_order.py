#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ranking dispatch order/ merit order.

@author: jinxi
"""
#import pandas as pd
#pd.set_option('display.precision',3)
#import numpy as np

def fun_rank_dispatch(df_pp_new):
    ranked_dispatch = df_pp_new.query('capacity_available_KW != 0') 
    #ranked_dispatch.is_copy = False
    #print(ranked_dispatch)
    #ranked_dispatch = ranked_dispatch.groupby('plant_type').agg({'capacity_available_KW':'sum','marginal_cost':'mean'})
    ranked_dispatch.sort_values('marginal_cost',inplace=True)
    ranked_dispatch.reset_index(drop=False,inplace=True)


    return ranked_dispatch
