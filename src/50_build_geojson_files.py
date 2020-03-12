# -*- coding: utf-8 -*-
"""
Simply converts all of the generated data to geoJSON for use in MapBox.

@author: Josh P. Sawyer
"""

import arcpy
from pyhere import here
import logging
import extarc as ea

# set environment flags - we don't want Z / M, we do want overwrite on
# the final product
arcpy.env.outputZFlag = "Disabled"
arcpy.env.outputMFlag = "Disabled"
arcpy.env.overwriteOutput = True

arcpy.env.scratchWorkspace = str(here("results", "scratch"))

if __name__ == "__main__":
    ea.logger.setup_logging(here("src", "logging.yaml"))
    logger = logging.getLogger(__name__)

    logger.info("Building geoJSON files")
    
    logger.info("Building dam file")
    # the location of our snapped dam data
    dams = str(here("results", "results.gdb", "snapped_aoi_dams"))
    
    output_dir = here("results")
    
    # output to geojson
    arcpy.FeaturesToJSON_conversion(
        dams,
        str(output_dir / "dams_gj.geojson"),
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