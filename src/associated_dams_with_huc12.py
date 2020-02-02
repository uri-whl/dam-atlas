# -*- coding: utf-8 -*-
"""
Created on 2020-01-16

@author: Josh P. Sawyer
"""

import os.path
import extarc as ea

import arcpy
from pyprojroot import here

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

arcpy.env.scratchWorkspace = str(here('./results/scratch'))

if __name__ == "__main__":
    ea.logger.setup_logging(here("./src/logging.yaml"))
    ea.logger.send("associating dams with huc12")
    
    huc12s = []
    
    # there are 10 nhdplus datasets so we combine their huc12 files
    for huc in nhd_hucs:
        nhd_loc = str(here('./data/nhdplus_h/'))
        nhd_gdb = nhd_gdb_p + huc + nhd_gdb_s
        huc_path = 'WBD' + os.path.sep + 'WBDHU12'
        huc12 = os.path.join(nhd_loc, nhd_gdb, huc_path)
    
        # error is throwing merging datasets - there's something going on with
        # the field names are values, but we only care about the HUC12, so get
        # rid of everything else
    
        huc12_clean = ea.object.get_unused_scratch_gdb_obj()
        
        arcpy.CopyFeatures_management(huc12, huc12_clean)

        fields_to_keep = ["HUC12"]
        fields_to_keep.append(ea.table.get_oid_fieldname(huc12_clean))
        
        fieldList = arcpy.ListFields(huc12_clean)
        
        fields_to_kill = []
        
        for field in fieldList:
            if not field.required and field.name not in fields_to_keep:
                fields_to_kill.append(str(field.name))
        
        arcpy.DeleteField_management(huc12_clean, fields_to_kill)

        huc12s.append(huc12_clean)
      
    m_huc12s = ea.object.get_unused_scratch_gdb_obj()
    
    arcpy.Merge_management(huc12s, m_huc12s)
      
    # use identify to associated dam FIDs with huc12s
    merged_dams = str(here('./results/results.gdb/merged_dams', warn=False))
    
    m_dam_huc12s = ea.object.get_unused_scratch_gdb_obj() 
    
    arcpy.Identity_analysis(merged_dams, m_huc12s, m_dam_huc12s)
    
    # ma, ct and vt have some dams that don't fall in a huc12 - they're not 
    # a concern right now but maybe at some point that needs to be fixed...
    
    # now add huc10 - huc4
    
    arcpy.AddField_management(m_dam_huc12s, "HUC10", "TEXT", field_length=10)
    arcpy.AddField_management(m_dam_huc12s, "HUC8", "TEXT", field_length=8)
    arcpy.AddField_management(m_dam_huc12s, "HUC6", "TEXT", field_length=6)
    arcpy.AddField_management(m_dam_huc12s, "HUC4", "TEXT", field_length=4)
    
    field_names = ["HUC12", "HUC10", "HUC8", "HUC6", "HUC4"]
    
    with arcpy.da.UpdateCursor(m_dam_huc12s, field_names) as cursor:
        for row in cursor:
            row[1] = row[0][:10]
            row[2] = row[0][:8]
            row[3] = row[0][:6]
            row[4] = row[0][:4]
                            
            cursor.updateRow(row)


    # save to results folder
    output_loc = str(here('./results/results.gdb/merged_dams_hucs', warn=False))
    
    arcpy.CopyFeatures_management(m_dam_huc12s, output_loc)

    ea.logger.send("HUC association finish")
