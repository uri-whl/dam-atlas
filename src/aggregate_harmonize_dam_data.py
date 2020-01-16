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
from arcutils import arcutils as au
from arcutils.common_logger import setup_logging
import logging
from datetime import date
import pandas as pd

# set environment flags - we don't want Z / M, we do want overwrite on
# the final product
arcpy.env.outputZFlag = "Disabled"
arcpy.env.outputMFlag = "Disabled"
arcpy.env.overwriteOutput = True

# canonical fields are those fields that we want in the final dataset
# anything that's not a canonical field gets removed at the end of combination

canonical_fields = [
    'NAT_ID',
    'STATE',
    'DAM_NAME',
    'ALT_NAME'
    'TOWN',
    'STATUS',
    'HAZ_CLASS',
    'SOURCE'
]

# paths to the shapefiles containing dam data
dams = {
    'ct': str(here('./data/ct_dams/DAM.shp')),
    'ma': str(here('./data/ma_dams/DAMS_PT.shp')),
    'me': str(here('./data/me_dams/impounds.shp')),
    'nh': str(here('./data/nh_dams/damsnh.shp')),
    'ri': str(here('./data/ri_dams/Dams.shp')),
    'vt': str(here('./data/vt_dams/Dams.shp')),
}

# where the data was downloaded from - make it easier for the end user
dam_sources = {
    'ct': "ct gis",
    'ma': "ma gis",
    'me': "me gis",
    'nh': "nh gis",
    'ri': "ri gis",
    'vt': "vt gis",
}

# the date you downloaded the data
date_data_downloaded = str(date(2020, 1, 16))

# empty dictionary for reprojected dams
dams_wgs84 = {
}

if __name__ == "__main__":
    # create a logger
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("Aggregating dam data to common file")

    wgs84 = au.get_sr_wgs84()
    
    # reproject all data into wgs84
    
    for key, value in dams.items():
        dams_wgs84[key] = au.get_unused_scratch_fc()
        arcpy.Project_management(value, dams_wgs84[key], wgs84)
        
        # alter the name of each field to avoid merge collisions
        field_list = arcpy.ListFields(dams_wgs84[key])
        
        for field in field_list:
            if (not field.required):
                new_field_name = field.name + "_" + key.upper()
                logger.debug("current field name being altered: " + new_field_name)
                arcpy.AlterField_management(dams_wgs84[key], field.name, new_field_name, "")

        
        # add state field & populate        
        arcpy.AddField_management(dams_wgs84[key], "STATE",
                                  "TEXT", field_length = 2)
        
        arcpy.CalculateField_management(dams_wgs84[key], "STATE",
                                        "'" + key.upper() + "'", "PYTHON3")


        # add source detail for posterity, as well as when last accessed
        arcpy.AddField_management(dams_wgs84[key], "DATA_SOURCE",
                                  "TEXT")
        
        arcpy.CalculateField_management(dams_wgs84[key], "DATA_SOURCE",
                                        "'" + dam_sources[key] + "'", "PYTHON3")
        
        arcpy.AddField_management(dams_wgs84[key], "DATE_DOWNLOAD",
                                  "TEXT")
        
        arcpy.CalculateField_management(dams_wgs84[key], "DATE_DOWNLOAD",
                                        "'" + date_data_downloaded + "'", "PYTHON3")


    
    # combine datasets
    
    merged_dams = au.get_unused_scratch_fc()
    arcpy.Merge_management(list(dams_wgs84.values()), merged_dams)

    # add canonical fields
    
    # move state specific fields to canonical fields & perform calcs
    
    # discard all non-canonical fields
    field_list = arcpy.ListFields(merged_dams)
    fields_to_discard = []
    
    for field in field_list:
        if (not field.required and not field.name in canonical_fields):
                fields_to_discard.append(field.name)

    arcpy.DeleteField_management(merged_dams, fields_to_discard)
    

    # add x / y & rename to sane names
    arcpy.AddXY_management(merged_dams)
    arcpy.AlterField_management(merged_dams, "POINT_X", "LONGITUDE", "")
    arcpy.AlterField_management(merged_dams, "POINT_Y", "LATITUDE", "")
    
    results_dir = str(here('./results/'))
    output_gdb = 'results.gdb'
    
    # check if there's a results gdb and create if not
    if (not arcpy.Exists(os.path.join(results_dir, output_gdb))):
        arcpy.CreateFileGDB_management(results_dir, output_gdb)
    
    # save to results folder
    output_loc = str(here('./results/results.gdb/merged_dams', warn=False))
    
    arcpy.CopyFeatures_management(merged_dams, output_loc)
