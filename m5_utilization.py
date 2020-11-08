#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#  hourly revenue and profit.py
#  @author: jinxi


def fun_pp_utilization(marginal_cost,last_supply_percent,eq_price):
    pp_utilization = 1
    if marginal_cost == eq_price: ##last supply type.
        pp_utilization = last_supply_percent
    if marginal_cost < eq_price:
        pp_utilization = 1 ##fully running.
    if marginal_cost > eq_price:
        pp_utilization = 0 ##not running.

   
    return pp_utilization

