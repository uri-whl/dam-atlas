# -*- coding: utf-8 -*-
"""
Created on 2020-01-16

@author: Josh P. Sawyer
"""

import os.path

import extarc as ea
import arcpy
from pyhere import here
import logging

# set environment flags - we don't want Z / M, we do want overwrite on
# the final product
arcpy.env.outputZFlag = "Disabled"
arcpy.env.outputMFlag = "Disabled"
arcpy.env.overwriteOutput = True

nhd_gdb_p = "NHDPLUS_H_"
nhd_gdb_s = "_HU4_GDB.gdb"

nhd_hucs = [
    '0107',
    '0108',
    '0109',
    '0110'
]

arcpy.env.scratchWorkspace = str(here('./results/scratch'))

if __name__ == "__main__":
    ea.logger.setup_logging(here("src", "logging.yaml"))
    logger = logging.getLogger(__name__)
   
    logger.info("Snapping dams to NHD HR Flowline")

    # starting with combined dataset
    merged_dams = str(here("results", "results.gdb", "merged_dams_v2"))
    
    # make a copy - snap edits in place
    dam_copy = ea.obj.get_unused_scratch_gdb_obj()
    arcpy.CopyFeatures_management(merged_dams, dam_copy)
           
    flowlines = []
    
    # snap to flowline of nhd - there are 10 nhdplus datasets so we combine them
    for huc in nhd_hucs:
        nhd_loc = here("data", "nhdplus_h")
        nhd_gdb = nhd_gdb_p + huc + nhd_gdb_s
        flowline = nhd_loc / nhd_gdb / "Hydrography" / "NHDFlowline"
        
        flowlines.append(str(flowline))
    
    m_flowline = ea.obj.get_unused_scratch_gdb_obj()
    arcpy.Merge_management(flowlines, m_flowline)
    
    # the datasets in consideration are huge - but we can simplify them, as not
    # every point is near a line, and not every line is near a point.
    
    dam_sub_lyr = "dam_sub"
    flow_sub_lyr = "flow_sub"
    
    subset_distance = "80 Meters"
    snap_distance = "60 Meters"
    
    arcpy.MakeFeatureLayer_management(m_flowline, flow_sub_lyr)
    arcpy.MakeFeatureLayer_management(dam_copy, dam_sub_lyr)

    arcpy.SelectLayerByLocation_management(dam_sub_lyr,
               "WITHIN_A_DISTANCE", flow_sub_lyr, subset_distance,
               "NEW_SELECTION", "NOT_INVERT")

    arcpy.SelectLayerByLocation_management(flow_sub_lyr,
               "WITHIN_A_DISTANCE", dam_sub_lyr, subset_distance,
               "NEW_SELECTION", "NOT_INVERT")

    dam_sub = ea.obj.get_unused_scratch_gdb_obj()
    arcpy.CopyFeatures_management(dam_sub_lyr, dam_sub)
    
    flow_sub = ea.obj.get_unused_scratch_gdb_obj()
    arcpy.CopyFeatures_management(flow_sub_lyr, flow_sub)

    # data's subsetted, now snap
    arcpy.Snap_edit(dam_sub, [[flow_sub, "EDGE", snap_distance]])
    
    # interesect with flowline to get only those that were snapped
    dam_snapped = str(here("results", "results.gdb", "all_snapped_dams_v2"))
    
    arcpy.Intersect_analysis([dam_sub, flow_sub],
                             dam_snapped)

    # add new x / y & rename to sane names
    arcpy.AddXY_management(dam_snapped)
    # rename old lat / long
    arcpy.AlterField_management(dam_snapped, "LONGITUDE", "LONG_PRESNAP", "LONG_PRESNAP")
    arcpy.AlterField_management(dam_snapped, "LATITUDE", "LAT_PRESNAP", "LAT_PRESNAP")
    arcpy.AlterField_management(dam_snapped, "POINT_X", "LONGITUDE", "LONGITUDE")
    arcpy.AlterField_management(dam_snapped, "POINT_Y", "LATITUDE", "LATITUDE")
    
    logger.info("finished snapping dams")
    logger.info("results in {}".format(dam_snapped))