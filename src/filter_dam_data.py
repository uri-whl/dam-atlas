# -*- coding: utf-8 -*-

"""
Created 2020-01-16

While aggregate_harmonize_dam_data.py combines the datasets in an unopinionated
way, there's a lot of junk in these datasets. For instance, there are multiple
dams that have 0,0 as their coordinates in the dam datasets. We do some
prefiltering here.

@author: Josh P. Sawyer
"""

import sys
import os.path

# self append to grab arcutils module
sys.path.append(os.path.dirname(__file__))

import arcpy
from pyprojroot import here
from arcutils.common_logger import setup_logging
import logging

# set environment flags - we don't want Z / M, we do want overwrite on
# the final product
arcpy.env.outputZFlag = "Disabled"
arcpy.env.outputMFlag = "Disabled"
arcpy.env.overwriteOutput = True

# paths to the shapefiles containing dam data
dams = {
    'CT': str(here('./data/ct_dams/DAM.shp')),
    'MA': str(here('./data/ma_dams/DAMS_PT.shp')),
    'ME': str(here('./data/me_dams/impounds.shp')),
    'NH': str(here('./data/nh_dams/damsnh.shp')),
    'RI': str(here('./data/ri_dams/Dams.shp')),
    'VT': str(here('./data/vt_dams/Dams.shp')),
}

dams_f = {
    'CT': str(here('./results/results.gdb/ct_dams_f', warn=False)),
    'MA': str(here('./results/results.gdb/ma_dams_f', warn=False)),
    'ME': str(here('./results/results.gdb/me_dams_f', warn=False)),
    'NH': str(here('./results/results.gdb/nh_dams_f', warn=False)),
    'RI': str(here('./results/results.gdb/ri_dams_f', warn=False)),
    'VT': str(here('./results/results.gdb/vt_dams_f', warn=False))
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
    # create a logger
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("Filtering dam data for known issues")

    for state in list(dams.keys()):
        arcpy.MakeFeatureLayer_management(dams[state], layer[state])
    
    logger.info("Filtering NH dams for 0,0 coordinates")
    
    arcpy.SelectLayerByAttribute_management(
        layer['NH'], "NEW_SELECTION", '"LATITUDE" <> 0 AND "LONGITUDE" <> 0')
    
    results_dir = str(here('./results/'))
    output_gdb = 'results.gdb'
    
    # check if there's a results gdb and create if not
    if (not arcpy.Exists(os.path.join(results_dir, output_gdb))):
        arcpy.CreateFileGDB_management(results_dir, output_gdb)
    
    logger.info("Writing filtered data")
    
    # writing filtered data
    for state in list(dams.keys()):
        arcpy.CopyFeatures_management(layer[state], dams_f[state])
   
    
