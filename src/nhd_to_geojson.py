# -*- coding: utf-8 -*-
"""
Created on 2020-03-16

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

# prefix and suffix for nhd gdbs
nhd_gdb_p = "NHDPLUS_H_"
nhd_gdb_s = "_HU4_GDB.gdb"

# these four nhds cover all of RI and almost all of MA + CT
# leaving a small amount in the west out.

nhd_hucs = [
    '0107',
    '0108',
    '0109',
    '0110'
]

if __name__ == "__main__":
    ea.logger.setup_logging(here("src", "logging.yaml"))
    logger = logging.getLogger(__name__)
    logger.info("converting nhd data to geojson for upload to mapbox")

    for huc in nhd_hucs:
        logger.info("exporting data for huc " + huc)

        nhd_loc = here("data", "nhdplus_h")
        nhd_gdb = nhd_gdb_p + huc + nhd_gdb_s

        flowline = str(nhd_loc / nhd_gdb / "Hydrography" / "NHDFlowline")
        flowline_scr = ea.obj.get_unused_scratch_gdb_obj()
        flowline_vaa =  str(nhd_loc / nhd_gdb / "NHDPlusFlowlineVAA")

        arcpy.CopyFeatures_management(flowline, flowline_scr)

        arcpy.JoinField_management(
            flowline_scr,
            "NHDPlusID",
            flowline_vaa,
            "NHDPlusID",
            ["StreamOrder"]
        )

        flowline_f = "flowline_f"
        arcpy.MakeFeatureLayer_management(flowline_scr, flowline_f)
        arcpy.SelectLayerByAttribute_management(
            flowline_f,
            'NEW_SELECTION',
            "FType NOT IN( 566 )"
        )

        arcpy.FeaturesToJSON_conversion(
            flowline_f,
            str(here("results/geojson/nhd_flowlines/flowline_" + huc + ".geojson")),
            geoJSON = "GEOJSON",
            outputToWGS84 = "WGS84"
        )

        waterbody = str(nhd_loc / nhd_gdb / "Hydrography" / "NHDWaterbody")
        waterbody_f = "waterbody_f"
        arcpy.MakeFeatureLayer_management(waterbody, waterbody_f)
        arcpy.SelectLayerByAttribute_management(
            waterbody_f,
            'NEW_SELECTION',
            "FType IN( 390, 436 )"
        )
        arcpy.FeaturesToJSON_conversion(
            waterbody_f,
            str(here("results/geojson/nhd_wbs/wbs_" + huc + ".geojson")),
            geoJSON = "GEOJSON",
            outputToWGS84 = "WGS84"
        )

        huc8 = str(nhd_loc / nhd_gdb / "WBD" / "WBDHU8")
        huc10 = str(nhd_loc / nhd_gdb / "WBD" / "WBDHU10")
        huc12 = str(nhd_loc / nhd_gdb / "WBD" / "WBDHU12")

        arcpy.FeaturesToJSON_conversion(
            huc8,
            str(here("results/geojson/nhd_huc8/huc8_" + huc + ".geojson")),
            geoJSON = "GEOJSON",
            outputToWGS84 = "WGS84"
        )
        arcpy.FeaturesToJSON_conversion(
            huc10,
            str(here("results/geojson/nhd_huc10/huc10_" + huc + ".geojson")),
            geoJSON = "GEOJSON",
            outputToWGS84 = "WGS84"
        )
        arcpy.FeaturesToJSON_conversion(
            huc12,
            str(here("results/geojson/nhd_huc12/huc12_" + huc + ".geojson")),
            geoJSON = "GEOJSON",
            outputToWGS84 = "WGS84"
        )
    logger.info("conversion complete")