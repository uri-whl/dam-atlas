# -*- coding: utf-8 -*-
"""
Created on Tue Jan 14 15:20:42 2020

@author: Josh
"""

import arcpy

# starting with combined dataset

# snap to flowline of nhd - there are 10 nhdplus datasets that are being considered
# so iteratively snap against each one, only retrying those points that did not snap

# alternatively, subset the data by 

# add x, y again

# compare

# flag the ones that were snapped succesfully