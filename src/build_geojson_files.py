# -*- coding: utf-8 -*-
"""
Simply converts all of the generated data to geoJSON for use in MapBox.

@author: Josh P. Sawyer
"""

import os.path

import arcpy
from pyprojroot import here
import logging

# set environment flags - we don't want Z / M, we do want overwrite on
# the final product
arcpy.env.outputZFlag = "Disabled"
arcpy.env.outputMFlag = "Disabled"
arcpy.env.overwriteOutput = True

if __name__ == "__main__":
    logger = logging.getLogger(__name__)

    logger.info("Building geoJSON files")
    
    logger.info("Building dam file")
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
    # logger.info("Building dam watershed file")
    
    # the location of the various NHD watersheds
    # logger.info("Building NHD watershed file")
    
    logger.info("geoJSON files complete")