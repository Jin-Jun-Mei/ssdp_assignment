#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
"""
attributes of power plants that can be invested.

@author: jinxi
"""

class Plants(): ##Capitalized names refer to classes
    def __init__(self, plant_type, capacity, running_cost, investment_cost, lifetime, emission_intensity):
        self.plant_type = plant_type 
        self.capacity = capacity ## unit:KWe
        self.running_cost = running_cost ## unit: cent/kWh
        self.investment_cost = investment_cost ## unit: cent/KW
        self.lifetime = lifetime ## unit:year
        self.emission_intensity = emission_intensity ##(emssion intensity), unit: ton CO2eq/kWh
        

coal = Plants ('coal', 500*10**3, 2, 145000, 40, 0.001) ## unit of capacity: KW
gas = Plants ( 'gas', 500*10**3, 4.5, 90000, 30, 0.00045)
solar = Plants ( 'solar', 500*10**3, 0, 80000, 25, 0)
wind = Plants ('wind', 500*10**3, 0, 150000, 25, 0)
CN_baseload = Plants ('CN_baseload', 500*10**3, 1.0, 600000, 40, 0)
biomass_1 = Plants ('biomass', 500*10**3, 6.1, 90000, 30, 0) 
# ~ biomass_2 = Plants ('biomass', 500*10**3, 6.1, 60000, 30, 0) 
# ~ biomass_3 = Plants ('biomass', 500*10**3, 9.0, 60000, 30, 0) 
# ~ biomass_4 = Plants ('biomass', 500*10**3, 200, 90000, 30, 0) 

biomass = biomass_1
pp_list = list((CN_baseload,coal,gas,solar,wind))
# ~ fuel_list = list((biomass,CN_baseload,coal,gas,solar,wind))
fuel_list = list((CN_baseload,coal,gas,solar,wind))

r = 0.08
CRF =  {}
for pp in pp_list:
    CRF[str(pp.plant_type)] = r*(1+r)**pp.lifetime/((1+r)**pp.lifetime-1)

# ~ print(CRF)
