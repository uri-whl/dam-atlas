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

# set environment flags - we don't want Z / M, we do want overwrite on
# the final product
arcpy.env.outputZFlag = "Disabled"
arcpy.env.outputMFlag = "Disabled"
arcpy.env.overwriteOutput = True

nhd_gdb_p = "NHDPLUS_H_"
nhd_gdb_s = "_HU4_GDB.gdb"

nhd_hucs = [
    '0101',
    '0102',
    '0103',
    '0104',
    '0105',
    '0106',
    '0107',
    '0108',
    '0109',
    '0110'
]

if __name__ == "__main__":
    # create a logger
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("Snapping dams to NHD HR Flowline")

    # starting with combined dataset
    merged_dams = str(here('./results/results.gdb/merged_dams', warn=False))
    
    # make a copy - snap edits in place
    dam_copy = au.get_unused_scratch_fc()
    arcpy.CopyFeatures_management(merged_dams, dam_copy)
           
    flowlines = []
    
    # snap to flowline of nhd - there are 10 nhdplus datasets so we combine them
    for huc in nhd_hucs:
        nhd_loc = str(here('./data/nhdplus_h/'))
        nhd_gdb = nhd_gdb_p + huc + nhd_gdb_s
        flow_path = 'Hydrography' + os.path.sep + 'NHDFlowline'
        flowline = os.path.join(nhd_loc, nhd_gdb, flow_path)
    
        flowlines.append(flowline)
    
    m_flowline = au.get_unused_scratch_fc()
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

    dam_sub = au.get_unused_scratch_fc()
    arcpy.CopyFeatures_management(dam_sub_lyr, dam_sub)
    
    flow_sub = au.get_unused_scratch_fc()
    arcpy.CopyFeatures_management(flow_sub_lyr, flow_sub)

    # data's subsetted, now snap
    arcpy.Snap_edit(dam_sub, [[flow_sub, "EDGE", snap_distance]])
    
    # interesect with flowline to get only those that were snapped
    dam_snapped = str(here('./results/results.gdb/dams_snapped', warn=False))
    
    arcpy.Intersect_analysis([dam_sub, flow_sub],
                             dam_snapped)
