#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  switch to biofule

def func_switch_bio(df,bio_run_cost):
    if df.loc[df.plant_type == 'gas'].marginal_cost.values > bio_run_cost:
        index_gas = df.loc[df.plant_type == 'gas'].index
        df.at[index_gas, 'marginal_cost'] = bio_run_cost ## switch to biomass.
        df.at[index_gas, 'plant_type'] = 'biomass'
            
    return df
