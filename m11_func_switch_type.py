#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  switch plant_type

def func_switch_type(df,original_type,desired_type):
    index = df.loc[df.plant_type == original_type].index
    df.at[index, 'plant_type'] = desired_type ## switch name of biomass to gas.
    return df
    
