# -*- coding: utf-8 -*-
"""
Created on Tue Jan 14 15:20:42 2020

@author: Josh
"""
import sys
import os.path

# self append to grab arcutils module
sys.path.append(os.path.dirname(__file__))

import arcpy
from pyprojroot import here
import logging

# set environment flags - we don't want Z / M, we do want overwrite on
# the final product
arcpy.env.outputZFlag = "Disabled"
arcpy.env.outputMFlag = "Disabled"
arcpy.env.overwriteOutput = True

if __name__ == "__main__":
    # the location of our snapped dam data
    dams = str(here('./results/results.gdb/merged_dams', warn=False))
    
    output_dir = str(here('./results/', warn=False))
    
    # output to geojson
    arcpy.FeaturesToJSON_conversion(
        dams,
        os.path.join(output_dir, "dams_gj.geojson"),
        "FORMATTED",
        "NO_Z_VALUES",
        "NO_M_VALUES",
        "GEOJSON",
        "WGS84"
    )
    
    # the location of the dam-specific watersheds
    
    # the location of the various NHD watersheds