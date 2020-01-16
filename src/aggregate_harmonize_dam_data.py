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

canonical_fields = {
    'NAT_ID' : 'TEXT',
    'STATE' : 'TEXT',
    'DAM_NAME' : 'TEXT',
    'ALT_NAME' : 'TEXT',
    'TOWN' : 'TEXT',
    'STATUS' : 'TEXT',
    'HAZ_CLASS' : 'TEXT',
    'SOURCE' : 'TEXT',
    'DATE_DOWNLOAD' : 'TEXT',
    'DATA_SOURCE' : 'TEXT'
}

# paths to the shapefiles containing dam data
dams = {
    'CT': str(here('./data/ct_dams/DAM.shp')),
    'MA': str(here('./data/ma_dams/DAMS_PT.shp')),
    'ME': str(here('./data/me_dams/impounds.shp')),
    'NH': str(here('./data/nh_dams/damsnh.shp')),
    'RI': str(here('./data/ri_dams/Dams.shp')),
    'VT': str(here('./data/vt_dams/Dams.shp')),
}

# where the data was downloaded from - make it easier for the end user
dam_sources = {
    'CT': "ct gis",
    'MA': "ma gis",
    'ME': "me gis",
    'NH': "nh gis",
    'RI': "ri gis",
    'VT': "vt gis",
}

state_to_canonical_map = {
    'NAT_ID' : {
        'VT' : {
            'name': 'NatID',
        },
        'ME' : {
            'name': 'ID',
        },
        'MA' : {
            'name': 'NATID',
        },
        'NH' : {
            'name': 'NATDAMID',
        },
    },
    'DAM_NAME': {  
        'VT' : {
            'name': 'DamName',
        },
        'RI' : {
            'name': 'NAME',
        },
        'CT' : {
            'name': 'DAM_NAME',
        }, 
        'ME' : {
            'name': 'NAME',
        },
        'MA' : {
            'name': 'DAMNAME',
        },
        'NH' : {
            'name': 'NAME',
        },
    }
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
                                        "'" + key + "'", "PYTHON3")


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
    for k, v in canonical_fields.items():
        arcpy.AddField_management(merged_dams, k, v)
    
    
    # populated canonical from state fields
    field_list = arcpy.ListFields(merged_dams)
    field_names = [field.name for field in field_list]
    
    # there's a big assumption here - that this entire script is being run at
    # once and not piece meal. there's no checking to verify that the fields
    # actually exist in the attribute table, it's assuming that they're there.
    with arcpy.da.UpdateCursor(merged_dams, field_names) as cursor:
        for row in cursor:
            for field in list(canonical_fields.keys()):
                # not every field is mapped - some are added after the fact or
                # calculated in a different way
                if field in state_to_canonical_map:
                    # not every state has a map populated
                    state_field_i = field_names.index('STATE')
                    if row[state_field_i] in state_to_canonical_map[field]:
                        # we've found a state match for the canon field
                        
                        # construct the name of the state field
                        sfield_name = state_to_canonical_map[field][row[state_field_i]]['name'] + "_" + row[state_field_i]
                        
                        # get state field column index
                        sfield_i = field_names.index(sfield_name)
                        
                        # get destination field column index
                        dfield_i = field_names.index(field)
                        
                        if 'conversion_factor' in state_to_canonical_map[field][row[state_field_i]]:
                            row[dfield_i] = row[sfield_i] * state_to_canonical_map[field][row[state_field_i]]['conversion_factor']
                        else:
                            row[dfield_i] = row[sfield_i]
                            
                        cursor.updateRow(row)

                            
            
    
    # discard all non-canonical fields
    field_list = arcpy.ListFields(merged_dams)
    fields_to_discard = []
    canonical_names = list(canonical_fields.keys())
    
    for field in field_list:
        if (not field.required and not field.name in canonical_names):
                fields_to_discard.append(field.name)

    arcpy.DeleteField_management(merged_dams, fields_to_discard)
    

    # add x / y & rename to sane names
    arcpy.AddXY_management(merged_dams)
    arcpy.AlterField_management(merged_dams, "POINT_X", "LONGITUDE", "LONGITUDE")
    arcpy.AlterField_management(merged_dams, "POINT_Y", "LATITUDE", "LATITUDE")
    
    results_dir = str(here('./results/'))
    output_gdb = 'results.gdb'
    
    # check if there's a results gdb and create if not
    if (not arcpy.Exists(os.path.join(results_dir, output_gdb))):
        arcpy.CreateFileGDB_management(results_dir, output_gdb)
    
    # save to results folder
    output_loc = str(here('./results/results.gdb/merged_dams', warn=False))
    
    arcpy.CopyFeatures_management(merged_dams, output_loc)
