# -*- coding: utf-8 -*-
"""
Created on Tue Jan 14 15:20:42 2020

The below script takes data files which describe dams within RI, MA and CT
as well as removed dams from the American Rivers project and RI DEM, and "munges"
them together. Specifically, it:

- Reprojects them into a common spatial reference (GCS NAD 83, same as NHD)
- Generates lat / long
- Loads all dam attribute tables as dataframes
- Loads removed dams as dataframes
- Loads NID data as dataframes
- Crosswalks attributes with column names
- Stacks all the data - i.e., merges all dataframes
- Re-creates this data as a feature class
- Saves it into a final GDB

In this way, all steps related to data crosswalking are preserved and reproducible.

@author: Josh P. Sawyer
"""

import arcpy
from pyhere import here
import logging
from datetime import date
import extarc as ea
import pandas as pd
import tempfile
import numpy as np

# set environment flags - we don't want Z / M, we do want overwrite on
# the final product
arcpy.env.outputZFlag = "Disabled"
arcpy.env.outputMFlag = "Disabled"
arcpy.env.overwriteOutput = True

arcpy.env.scratchWorkspace = str(here("results", "scratch"))

if __name__ == "__main__":
    ea.logger.setup_logging(here("src", "logging.yaml"))
    logger = logging.getLogger(__name__)
    
    logger.info("Aggregating dam data to common file started")

    input_fc = str(here("results", "results.gdb", "all_raw_dam_data"))

    # make a copy
    output_fc = str(here("results", "results.gdb", "reduced_dam_data"))

    arcpy.CopyFeatures_management(input_fc, output_fc)

    # drop everything but attributes of interest - for now
    attributes = [
        'year_completed',
        'nid_id',
        'state_id',
        'dam_name',
        'alt_name',
        'dam_type',
        'longitude',
        'latitude',
        'county',
        'town',
        'hazard',
        'state',
        'removed',
        'owntype1',
        'owntype2',
        'owntype3',
        'dam_height',
        'fish_passage_modification',
        'other_fish_passage_modification',
        'dam_atlas_id'
    ]


    # Use ListFields to get a list of field objects
    fieldObjList = arcpy.ListFields(output_fc)
 
    # Create an empty list that will be populated with field names        
    fieldNameList = []
 
    # For each field in the object list, add the field name to the
    #  name list.  If the field is required, exclude it, to prevent errors
    for field in fieldObjList:
        if not field.required and not field.name in attributes:
            fieldNameList.append(field.name)

    arcpy.DeleteField_management(output_fc, fieldNameList)

    # one last thing - the earlier data set manipulation has stripped field
    # types from the datasets so now they need to be added back in. everything
    # is currently a string, so we can simply change the non-string data types.

    int_fnames = [
        'year_completed',
        'dam_atlas_id'
    ]

    for field in int_fnames:
        # rename existing field
        field_tmp = field + "_tmp"
        arcpy.AlterField_management(
            output_fc,
            field,
            field_tmp,
            field_tmp
        )

        # add a integer field
        arcpy.AddField_management(
            output_fc,
            field,
            "LONG"
        )

        arcpy.CalculateField_management(
            output_fc,
            field,
            "!" + field_tmp + "!"
        )

        arcpy.DeleteField_management(output_fc, [field_tmp])


    float_fnames = [
        'longitude',
        'latitude',
        'dam_height',
    ]

    for field in float_fnames:
        # rename existing field
        field_tmp = field + "_tmp"
        arcpy.AlterField_management(
            output_fc,
            field,
            field_tmp,
            field_tmp
        )

        # add a float field
        arcpy.AddField_management(
            output_fc,
            field,
            "FLOAT"
        )

        arcpy.CalculateField_management(
            output_fc,
            field,
            "!" + field_tmp + "!"
        )

        arcpy.DeleteField_management(output_fc, [field_tmp])
