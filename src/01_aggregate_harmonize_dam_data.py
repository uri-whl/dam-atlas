# -*- coding: utf-8 -*-
"""
Created on Tue Jan 14 15:20:42 2020

The below script takes state dam data shapefiles and combines them into
one master dam data file, cross-walking the state-specific attributes into
a series of canonical field names (i.e., canonical for this dataset) for use
in various analyses. It's designed generally enough that you should be able
to take this script and apply it to any collection of state dam datasets that
you want to harmonize and aggregate.

@author: Josh P. Sawyer
"""

import arcpy
from pyhere import here
import logging
from datetime import date
import extarc as ea

# set environment flags - we don't want Z / M, we do want overwrite on
# the final product
arcpy.env.outputZFlag = "Disabled"
arcpy.env.outputMFlag = "Disabled"
arcpy.env.overwriteOutput = True

# canonical fields are those fields that we want in the final dataset
# anything that's not a canonical field gets removed at the end of combination

canonical_fields = {
    'NAT_ID' : 'TEXT',
    'STATE' : 'TEXT',
    'DAM_NAME' : 'TEXT',
    'ALT_NAME' : 'TEXT',
    'TOWN' : 'TEXT',
    'STATUS' : 'TEXT',
    'HAZ_CLASS' : 'TEXT',
    'SOURCE' : 'TEXT',
    'DATE_DOWNLOAD' : 'TEXT',
    'DATA_SOURCE' : 'TEXT'
}

# paths to the shapefiles containing dam data
dams = {
    'CT': str(here("results", "results.gdb", "ct_dams_f")),
    'MA': str(here("results", "results.gdb", "ma_dams_f")),
    'ME': str(here("results", "results.gdb", "me_dams_f")),
    'NH': str(here("results", "results.gdb", "nh_dams_f")),
    'RI': str(here("results", "results.gdb", "ri_dams_f")),
    'VT': str(here("results", "results.gdb", "vt_dams_f"))
}

# where the data was downloaded from - make it easier for the end user
dam_sources = {
    'CT': "ct gis",
    'MA': "ma gis",
    'ME': "me gis",
    'NH': "nh gis",
    'RI': "ri gis",
    'VT': "vt gis",
}

# this nested dictionary defines the relationship between state fields from the
# state specific shape files to the canonical field names - i.e., the crosswalk
# relationship. additionally, it defines any necessary conversion to bring them
# into common units, as sometimes state data is stored in feet or meters.
state_to_canonical_map = {
    'NAT_ID' : {
        'VT' : {
            'name': 'NatID',
        },
        'ME' : {
            'name': 'ID',
        },
        'MA' : {
            'name': 'NATID',
        },
        'NH' : {
            'name': 'NATDAMID',
        },
        'RI' : {
            'name': 'NID'
        }
    },
    'DAM_NAME': {  
        'VT' : {
            'name': 'DamName',
        },
        'RI' : {
            'name': 'NAME',
        },
        'CT' : {
            'name': 'DAM_NAME',
        }, 
        'ME' : {
            'name': 'NAME',
        },
        'MA' : {
            'name': 'DAMNAME',
        },
        'NH' : {
            'name': 'NAME',
        },
    }
}

# the date you downloaded the data
date_data_downloaded = str(date(2020, 1, 16))

# empty dictionary for reprojected dams
dams_wgs84 = {
}

arcpy.env.scratchWorkspace = str(here("results", "scratch"))

if __name__ == "__main__":
    ea.logger.setup_logging(here("src", "logging.yaml"))
    logger = logging.getLogger(__name__)
    
    logger.info("Aggregating dam data to common file started")

    wgs84 = ea.sr.get_sr_wgs84()
    
    logger.info("State data housekeeping")
    
    for key, value in dams.items():
        # reproject all data into wgs84
        dams_wgs84[key] = ea.obj.get_unused_scratch_gdb_obj()
        arcpy.Project_management(value, dams_wgs84[key], wgs84)
        
        # alter the name of each field to avoid merge collisions
        field_list = arcpy.ListFields(dams_wgs84[key])
        
        for field in field_list:
            if (not field.required):
                new_field_name = field.name + "_" + key.upper()
                logger.debug("current field name being altered: " + new_field_name)
                arcpy.AlterField_management(dams_wgs84[key], field.name, new_field_name, "")

        
        # add state field & populate        
        arcpy.AddField_management(dams_wgs84[key], "STATE",
                                  "TEXT", field_length = 2)
        
        arcpy.CalculateField_management(dams_wgs84[key], "STATE",
                                        "'" + key + "'", "PYTHON3")


        # add source detail for posterity, as well as when last accessed
        arcpy.AddField_management(dams_wgs84[key], "DATA_SOURCE",
                                  "TEXT")
        
        arcpy.CalculateField_management(dams_wgs84[key], "DATA_SOURCE",
                                        "'" + dam_sources[key] + "'", "PYTHON3")
        
        arcpy.AddField_management(dams_wgs84[key], "DATE_DOWNLOAD",
                                  "TEXT")
        
        arcpy.CalculateField_management(dams_wgs84[key], "DATE_DOWNLOAD",
                                        "'" + date_data_downloaded + "'", "PYTHON3")

    # combine datasets
    logger.info("Merging into one feature class")
        
    merged_dams = ea.obj.get_unused_scratch_gdb_obj()
    arcpy.Merge_management(list(dams_wgs84.values()), merged_dams)

    logger.info("Migrating state fields to canonical fields")

    # add canonical fields
    for k, v in canonical_fields.items():
        arcpy.AddField_management(merged_dams, k, v)
        
    # populate canonical from state fields
    field_list = arcpy.ListFields(merged_dams)
    field_names = [field.name for field in field_list]
    
    # there's a big assumption here - that this entire script is being run at
    # once and not piece meal. there's no checking to verify that the fields
    # actually exist in the attribute table, it's assuming that they're there.
    with arcpy.da.UpdateCursor(merged_dams, field_names) as cursor:
        for row in cursor:
            for field in list(canonical_fields.keys()):
                # not every field is mapped - some are added after the fact or
                # calculated in a different way
                if field in state_to_canonical_map:
                    # not every state has a map populated
                    state_field_i = field_names.index('STATE')
                    if row[state_field_i] in state_to_canonical_map[field]:
                        # we've found a state match for the canon field
                        
                        # construct the name of the state field
                        sfield_name = state_to_canonical_map[field][row[state_field_i]]['name'] + "_" + row[state_field_i]
                        
                        # get state field column index
                        sfield_i = field_names.index(sfield_name)
                        
                        # get destination field column index
                        dfield_i = field_names.index(field)
                        
                        if 'conversion_factor' in state_to_canonical_map[field][row[state_field_i]]:
                            row[dfield_i] = row[sfield_i] * state_to_canonical_map[field][row[state_field_i]]['conversion_factor']
                        else:
                            row[dfield_i] = row[sfield_i]
                            
                        cursor.updateRow(row)
    
    # discard all non-canonical fields
    field_list = arcpy.ListFields(merged_dams)
    fields_to_discard = []
    canonical_names = list(canonical_fields.keys())
    
    for field in field_list:
        if (not field.required and not field.name in canonical_names):
                fields_to_discard.append(field.name)

    arcpy.DeleteField_management(merged_dams, fields_to_discard)
    
    # we're going to add one last thing - a dam project ID field.
    # this will allow us to join these dams with other generated data as
    # FIDs in feature classes mutate
    
    dam_proj_id = "NEDAT_ID"
    
    oid_fname = "!" + ea.table.get_oid_fieldname(merged_dams) + "!"
    
    arcpy.AddField_management(merged_dams, dam_proj_id, "LONG")
    arcpy.CalculateField_management(merged_dams, dam_proj_id, oid_fname)
    
    # save to results folder
    output_loc = str(here("results", "results.gdb", "merged_dams"))
    
    arcpy.CopyFeatures_management(merged_dams, output_loc)

    logger.info("Aggreation finished")
    logger.info("Results in: {}".format(output_loc))
