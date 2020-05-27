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
    merged_dams = str(here("results", "results.gdb", "reduced_dam_data"))
    
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
    dam_intersection = ea.obj.get_unused_scratch_gdb_obj()
    
    # dams at an nhd vertex will actually double - an intersection with the end
    # will add a row. after intersection, dissolve on the fid of the dams...
    arcpy.Intersect_analysis(
        [dam_sub, flow_sub],
        dam_intersection,
        join_attributes="ONLY_FID"
    )

    dam_intersection_d = ea.obj.get_unused_scratch_gdb_obj()

    dam_sub_fid_str = 'FID_' + arcpy.Describe(dam_sub).name

    arcpy.Dissolve_management(
        dam_intersection,
        dam_intersection_d,
        [dam_sub_fid_str],
        "", 
        "SINGLE_PART"
    )

    # ...then join it back to the dams. duplicate rows
    # and noise in the attributes are gone
    dam_joined_table = arcpy.AddJoin_management(
        dam_intersection_d,
        dam_sub_fid_str,
        dam_sub,
        ea.table.get_oid_fieldname(dam_sub)
    )

    dam_snapped = str(here("results", "results.gdb", "all_snapped_dams_v2"))

    arcpy.CopyFeatures_management(dam_joined_table, dam_snapped)
    arcpy.DeleteField_management(dam_snapped, [dam_sub_fid_str])

    # all the ACTUAL names of fields don't match their aliases - ugh
    field_list = arcpy.ListFields(dam_snapped)

    for field in field_list:
        if (not field.required and field.aliasName != "OBJECTID" and field.name != field.aliasName):
            field_name = str(field.name)
            field_alias = str(field.aliasName)

            arcpy.AlterField_management(
                dam_snapped,
                field_name,
                field_alias,
                clear_field_alias = "CLEAR_ALIAS"
            )


    # add new x / y & rename to sane names
    arcpy.AddXY_management(dam_snapped)
    # rename old lat / long
    arcpy.AlterField_management(dam_snapped, "longitude", "long_presnap", "long_presnap")
    arcpy.AlterField_management(dam_snapped, "latitude", "lat_presnap", "lat_presnap")
    arcpy.AlterField_management(dam_snapped, "POINT_X", "longitude", "longitude")
    arcpy.AlterField_management(dam_snapped, "POINT_Y", "latitude", "latitude")
    
    logger.info("finished snapping dams")
    logger.info("results in {}".format(dam_snapped))