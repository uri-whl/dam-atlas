# -*- coding: utf-8 -*-
"""
Created on 2020-01-16

@author: Josh P. Sawyer
"""

import extarc as ea
import arcpy
from pyhere import here
import logging

# set environment flags - we don't want Z / M, we do want overwrite on
# the final product
arcpy.env.outputZFlag = "Disabled"
arcpy.env.outputMFlag = "Disabled"
arcpy.env.overwriteOutput = True

arcpy.env.scratchWorkspace = str(here("results", "scratch"))

if __name__ == "__main__":
    ea.logger.setup_logging(here("src", "logging.yaml"))
    logger = logging.getLogger(__name__)
    logger.info("associating dams with huc12")
    
    all_dams_hucs = str(here("results", "results.gdb", "all_snapped_dams_w_hucs_v2"))
    
    # make flayer, select only dams in RI OR in wsheds of interest, make copy
    
    dams_flayer = "dams_flayer"
    
    arcpy.MakeFeatureLayer_management(all_dams_hucs, dams_flayer)

    arcpy.SelectLayerByAttribute_management(
        dams_flayer,
        'NEW_SELECTION',
        "STATE = 'RI'"
    )
    
    arcpy.SelectLayerByAttribute_management(
        dams_flayer,
        'ADD_TO_SELECTION',
        "HUC8 = '01090004'",
        ""
    )

    arcpy.SelectLayerByAttribute_management(
        dams_flayer,
        'ADD_TO_SELECTION',
        "HUC8 = '01090005'",
        ""
    )
    
    arcpy.SelectLayerByAttribute_management(
        dams_flayer,
        'ADD_TO_SELECTION',
        "HUC8 = '01090003'"
    )
    
    # save to results folder
    output_loc = str(here("results", "dam_database.gdb", "dam_database"))
    
    arcpy.CopyFeatures_management(dams_flayer, output_loc)
    
    # also grab a csv for easy reference
    dams_df = ea.table.get_arcgis_table_as_df(output_loc)
    dams_df.to_csv(here("results", "dam_attributes_v2.csv"))
    