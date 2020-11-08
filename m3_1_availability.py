"""
availability module.
set availability of each type of plant.

"""

def fun_availability(plant_type,avail_solar,avail_wind):
    if plant_type == 'solar':
        availability = avail_solar
    elif plant_type == 'wind':
        availability = avail_wind
    else:
        availability = 1 
    
    return availability
