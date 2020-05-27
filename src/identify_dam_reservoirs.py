# -*- coding: utf-8 -*-

# Reservoir data were obtained from the NHD HR database using the same approach
 # that generated the NEST database. The reservoirs are identified by using the 
 # ArcGIS “Near” Tool, which is in the Proximity toolset. This tool was also used
 # in this analysis to find the nearest waterbody polygon (from the 
 # Hydrography/NHDWaterbody file in the NHD HR data package) within 30 meters
# of the dam location (as snapped to the NHD HR flowlines) and obtain data such
# as the surface area of the waterbody. If no waterbody was within 30 meters of
# the dam location, no reservoir information was included.



# During creation of the NEST database, the NHDPlusV2 Basin Delineator software (from horizon-systems.com) was used to delineate the watersheds draining to each dam location. This tool is not available to be used with NHD HR, so the ArcGIS “Watershed” tool in the Hydrology toolset was used instead. The flow direction raster (elev_source.gdb/fdr.tif) from the NHD HR raster data were used as the input. As the dam locations were already snapped to the NHD HR flowlines, the “Snap Pour Point” tool was not used before the “Watershed” tool.

"""
Created on 2020-02-08

@author: Josh P. Sawyer
"""

import extarc as ea
import logging
import arcpy
from pyhere import here
import sys

sys.path.append(str(here("src")))

nhd_hucs = [
    '0107',
    '0108',
    '0109',
    '0110'
]

# set environment flags - we don't want Z / M, we do want overwrite on
# the final product
arcpy.env.outputZFlag = "Disabled"
arcpy.env.outputMFlag = "Disabled"
arcpy.env.overwriteOutput = True

arcpy.env.scratchWorkspace = str(here('./results/scratch'))

nhd_gdb_p = "NHDPLUS_H_"
nhd_gdb_s = "_HU4_GDB.gdb"

if __name__ == "__main__":
    ea.logger.setup_logging(here("./src/logging.yaml"))
    logger = logging.getLogger(__name__)

    
    logger.info("identifying dam reservoirs")
    
    snapped_dams = str(here("results", "dam_database.gdb", "dam_database"))
    
    nhd_wbids = []
    
    for huc in nhd_hucs:
        nhd_loc = here("data", "nhdplus_h")
        nhd_gdb = nhd_gdb_p + huc + nhd_gdb_s
        huc12 = nhd_loc / nhd_gdb / "Hydrography" / "NHDWaterbody"
    
        # error is throwing merging datasets - there's something going on with
        # the field names are values, but we only care about the HUC12, so get
        # rid of everything else
    
        nhd_wbid = ea.obj.get_unused_scratch_gdb_obj()
        
        arcpy.CopyFeatures_management(str(huc12), nhd_wbid)

        fields_to_keep = [
            "Permanent_Identifier",
            "GNIS_ID",
            "GNIS_Name",
            "FType",
            "FCode",
            "NHDPlusID"
        ]
        
        fields_to_keep.append(ea.table.get_oid_fieldname(nhd_wbid))
        
        fieldList = arcpy.ListFields(nhd_wbid)
        
        fields_to_kill = []
        
        for field in fieldList:
            if not field.required and field.name not in fields_to_keep:
                fields_to_kill.append(str(field.name))
        
        arcpy.DeleteField_management(nhd_wbid, fields_to_kill)

        nhd_wbids.append(nhd_wbid)
      
    m_wbids = ea.obj.get_unused_scratch_gdb_obj()
    arcpy.Merge_management(nhd_wbids, m_wbids)
    
    logger.info("dataset merge complete, identifying reservoirs")
    
    # selecting water bodies near dams
    
    m_wbids_f = "m_wbids_f"
    arcpy.MakeFeatureLayer_management(m_wbids, m_wbids_f)
      
    # get all water bodies near dams
    arcpy.SelectLayerByLocation_management(
        m_wbids_f,
        "WITHIN_A_DISTANCE",
        snapped_dams,
        "60 Meters"
    )
    
    near_wbids = ea.obj.get_unused_scratch_gdb_obj()
    arcpy.CopyFeatures_management(m_wbids_f, near_wbids)
   
    # associating near bodies with dam IDs
    
    arcpy.Near_analysis(near_wbids, snapped_dams, "61 Meters")

    arcpy.JoinField_management(
        near_wbids,
        "NEAR_FID",
        snapped_dams,
        ea.table.get_oid_fieldname(snapped_dams), 
        "NEDAT_ID"
    )
    
    # discard near data
    arcpy.DeleteField_management(
        near_wbids, 
        ["NEAR_FID", "NEAR_DIST"]
    )

    # stash in final
    wbids_near_dams= str(here("results", "dam_database.gdb", "wbids_near_dams"))
    arcpy.CopyFeatures_management(near_wbids, wbids_near_dams)

    
    logger.info("identification complete")
    