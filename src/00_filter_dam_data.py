# -*- coding: utf-8 -*-

"""
Created 2020-01-16

While aggregate_harmonize_dam_data.py combines the datasets in an unopinionated
way, there's a lot of junk in these datasets. For instance, there are multiple
dams that have 0,0 as their coordinates in the dam datasets. Also, there are
several dams that have been removed and we need to pull them out without
affecting the original datasets. We do some prefiltering here.

@author: Josh P. Sawyer
"""

import arcpy
from pyhere import here
import extarc as ea
import logging

# set environment flags - we don't want Z / M, we do want overwrite on
# the final product
arcpy.env.outputZFlag = "Disabled"
arcpy.env.outputMFlag = "Disabled"
arcpy.env.overwriteOutput = True

# paths to the shapefiles containing dam data
dams = {
    'CT': str(here("data", "ct_dams", "DAM.shp")),
    'MA': str(here("data", "ma_dams", "DAMS_PT.shp")),
    'ME': str(here("data", "me_dams", "impounds.shp")),
    'NH': str(here("data", "nh_dams", "damsnh.shp")),
    'RI': str(here("data", "ri_dams", "Dams.shp")),
    'VT': str(here("data", "vt_dams", "Dams.shp")),
}

dams_f = {
    'CT': str(here("results", "results.gdb", "ct_dams_f")),
    'MA': str(here("results", "results.gdb", "ma_dams_f")),
    'ME': str(here("results", "results.gdb", "me_dams_f")),
    'NH': str(here("results", "results.gdb", "nh_dams_f")),
    'RI': str(here("results", "results.gdb", "ri_dams_f")),
    'VT': str(here("results", "results.gdb", "vt_dams_f"))
}

layer = {
    'CT': 'ct_dams_layer',
    'MA': 'ma_dams_layer',
    'ME': 'me_dams_layer',
    'NH': 'nh_dams_layer',
    'RI': 'ri_dams_layer',
    'VT': 'vt_dams_layer'
}


if __name__ == "__main__":
    ea.logger.setup_logging(here("src", "logging.yaml"))
    logger = logging.getLogger(__name__)
    
    logger.info("Filtering dam data for known issues")

    for state in list(dams.keys()):
        arcpy.MakeFeatureLayer_management(dams[state], layer[state])
    
    logger.info("Filtering NH dams for 0,0 coordinates")
    
    # get rid of erroneous dams from in the new hampshire data set
    arcpy.SelectLayerByAttribute_management(
        layer['NH'], "NEW_SELECTION", '"LATITUDE" <> 0 AND "LONGITUDE" <> 0')
    
    results_dir = here("results")
    output_gdb = 'results.gdb'
    
    # check if there's a results gdb and create if not
    if (not results_dir.joinpath(output_gdb).exists()):
        arcpy.CreateFileGDB_management(str(results_dir), output_gdb)
    
    logger.info("Writing filtered data")
    
    # writing filtered data
    for state in list(dams.keys()):
        arcpy.CopyFeatures_management(layer[state], dams_f[state])
   
    
