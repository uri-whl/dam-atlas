# -*- coding: utf-8 -*-
"""
THIS SHOULD ONLY BE RUN ONCE!

Created on Tue Jan 14 15:20:42 2020

The below script takes data files which describe dams within RI, MA and CT
as well as removed dams from the American Rivers project and RI DEM, and "munges"
them together. Specifically, it:

- Reprojects them into a common spatial reference (GCS NAD 83, same as NHD)
- Generates lat / long
- Loads all dam attribute tables as dataframes
- Loads removed dams as dataframes
- Loads NID data as dataframes
- Crosswalks attributes with column names
- Stacks all the data - i.e., merges all dataframes
- Re-creates this data as a feature class
- Saves it into a final GDB

In this way, all steps related to data crosswalking are preserved and reproducible.

THAT SAID, THIS SHOULD ONLY BE RUN ONCE! If you edit it and re-run it, it will
potentially corrupt the order the dams appear in and so change the FIDs and
the dam atlas IDs. Instead, do your secondary data manipulation in 01_split*.py

@author: Josh P. Sawyer
"""

quit()

import arcpy
from pyhere import here
import logging
from datetime import date
import extarc as ea
import pandas as pd
import tempfile
import numpy as np

# set environment flags - we don't want Z / M, we do want overwrite on
# the final product
arcpy.env.outputZFlag = "Disabled"
arcpy.env.outputMFlag = "Disabled"
arcpy.env.overwriteOutput = True

arcpy.env.scratchWorkspace = str(here("results", "scratch"))

def clean_column_names(df):
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('(', '').str.replace(')', '')
    return df

def convert_ct_hazard(x):
    if (x == 'A'):
        return "Low"
    elif (x == 'BB'):
        return "Moderate"
    elif (x == 'B'):
        return "Significant"
    elif (x == 'C'):
        return "High"
    else:
        return x

def expand_nid_hazard_names(x):
    if (x == 'L'):
        return "Low"
    elif (x == 'S'):
        return "Significant"
    elif (x == 'H'):
        return "High"
    elif (x == 'U'):
        return "Undetermined"
    else:
        return "Not Available"

def expand_ct_ownership(x):
    if (x == 'D'):
        return "Owned by CT DEP"
    elif (x == 'F'):
        return "Federal government owned"
    elif (x == 'L'):
        return "Local (municipal) government owned"
    elif (x == 'P'):
        return "Privately owned"
    elif (x == 'S'):
        return "State goverment other than CT DEP owned"
    elif (x == 'U'):
        return "Utility owned"
    return x

if __name__ == "__main__":
    ea.logger.setup_logging(here("src", "logging.yaml"))
    logger = logging.getLogger(__name__)
    
    logger.info("Aggregating dam data to common file started")

    # NID data and NHD data are in NAD83 - make them all match when projecting
    nad83 = ea.sr.get_sr_nad83_gcs()

    # these dams are the only feature classes - reproject to nad83
    ri_dams = str(here("data/ri_dams/Dams.shp"))
    ct_dams = str(here("data/ct_dams/DAM.shp"))
    ma_dams = str(here("data/ma_dams/DAMS_PT.shp"))

    ct_dams_nad83 = ea.obj.get_unused_scratch_gdb_obj()
    arcpy.Project_management(ct_dams, ct_dams_nad83, nad83)

    # ct doesn't have an NID attribute - perform a spatial join to get a relationship
    # table so that they can be joined together

    # grab the CT NID xlsx
    ct_nid = pd.read_excel(here("data/NID_CT_U.xlsx"))

    # save it as a csv
    temp = tempfile.mkstemp(suffix=".csv") 
    ct_nid.to_csv(temp[1])

    # these are the column names in the csv containing lat / long data
    longitude_fname = "LONGITUDE"
    latitude_fname = "LATITUDE"

    ct_nid_flayer = "ct_nid_flayer"

    # load it as an XY layer
    arcpy.MakeXYEventLayer_management(
        temp[1],
        longitude_fname,
        latitude_fname,
        ct_nid_flayer,
        nad83
    )

    ct_nid_o = ea.obj.get_unused_scratch_gdb_obj()
    arcpy.CopyFeatures_management(ct_nid_flayer, ct_nid_o)

    ct_nid_map = ea.obj.get_unused_scratch_gdb_obj()

    arcpy.SpatialJoin_analysis(
        ct_dams_nad83,
        ct_nid_o,
        ct_nid_map,
        "JOIN_ONE_TO_ONE",
        "KEEP_ALL",
        "OBJECTID \"OBJECTID\" true true false 10 Long 0 10 ,First,#,C:\\proj\\code\\uri-whl\\dam-atlas\\data\\ct_dams\\DAM.shp,OBJECTID,-1,-1;NIDID \"NIDID\" true true false 8000 Text 0 0 ,Join,#,C:\\proj\\code\\uri-whl\\dam-atlas\\results\\scratch\\scratch.gdb\\next_fc146,NIDID,-1,-1",
        "WITHIN_A_DISTANCE",
        "3 Meters")

    # we've now got a map for NIDs and can join it to CT later,
    # finishing load ri / ma data

    ri_dams_nad83 = ea.obj.get_unused_scratch_gdb_obj()
    arcpy.Project_management(ri_dams, ri_dams_nad83, nad83)

    ma_dams_nad83 = ea.obj.get_unused_scratch_gdb_obj()
    arcpy.Project_management(ma_dams, ma_dams_nad83, nad83)

    # add x / y coordinates for each dam
    arcpy.AddXY_management(ri_dams_nad83)
    arcpy.AlterField_management(ri_dams_nad83, "POINT_X", "LONGITUDE", "LONGITUDE")
    arcpy.AlterField_management(ri_dams_nad83, "POINT_Y", "LATITUDE", "LATITUDE")

    arcpy.AddXY_management(ct_dams_nad83)
    arcpy.DeleteField_management(ct_dams_nad83, ["LATITUDE", "LONGITUDE"])
    arcpy.AlterField_management(ct_dams_nad83, "POINT_X", "LONGITUDE", "LONGITUDE")
    arcpy.AlterField_management(ct_dams_nad83, "POINT_Y", "LATITUDE", "LATITUDE")

    arcpy.AddXY_management(ma_dams_nad83)
    arcpy.DeleteField_management(ma_dams_nad83, ["LATITUDE", "LONGITUDE"])
    arcpy.AlterField_management(ma_dams_nad83, "POINT_X", "LONGITUDE", "LONGITUDE")
    arcpy.AlterField_management(ma_dams_nad83, "POINT_Y", "LATITUDE", "LATITUDE")

    # load the attribute tables of the reprojected data as dataframes
    ri_dam_df = ea.table.get_arcgis_table_as_df(ri_dams_nad83)
    ri_dam_df = clean_column_names(ri_dam_df)

    ct_dam_df = ea.table.get_arcgis_table_as_df(ct_dams_nad83)
    ct_dam_df = clean_column_names(ct_dam_df)

    ma_dam_df = ea.table.get_arcgis_table_as_df(ma_dams_nad83)
    ma_dam_df = clean_column_names(ma_dam_df)

    # load our ct->nid map
    ct_nid_map_df = ea.table.get_arcgis_table_as_df(ct_nid_map)
    ct_nid_map_df = clean_column_names(ct_nid_map_df)
    ct_nid_map_df = ct_nid_map_df.reset_index().drop(columns=['shape', 'OBJECTID_1', 'target_fid'])
    ct_nid_map_df = ct_nid_map_df.loc[ct_nid_map_df['join_count'] == 1].set_index('objectid').drop(columns=['join_count'])
    
    # join nids to ct data
    ct_dam_df = ct_dam_df.join(ct_nid_map_df)

    # drop some arcpy specific columns that will create noise
    ri_dam_df = ri_dam_df.reset_index().drop(columns=['shape', 'OBJECTID_1', 'objectid'])
    ct_dam_df = ct_dam_df.reset_index().drop(columns=['shape', 'objectid', 'OBJECTID_1'])
    ma_dam_df = ma_dam_df.reset_index().drop(columns=['shape', 'OBJECTID'])

    # bring in additional data from RI DEM for the RI dataset, join to RI
    ri_dams_dem = pd.read_csv(here("data/ri_dams/ri_dam_data.csv"))
    ri_dams_dem = clean_column_names(ri_dams_dem)
    # pad the state_id in ri_dams_dem with zeroes to match ri_dam_df (there's a non-numeric char in there)
    ri_dams_dem['state_id'] = ri_dams_dem['state_id'].apply('{:0>3}'.format)
    ri_dam_df = ri_dam_df.set_index('state_id').join(ri_dams_dem.set_index('state_id'), how='outer', rsuffix='_dem').reset_index()

    # there are three dams that are brought in that weren't in the shapefile,
    # copy there lat / longs over
    ri_dam_df['latitude'] = ri_dam_df['latitude'].where(ri_dam_df['latitude'] > 0, ri_dam_df['latitude_dem'])
    ri_dam_df['longitude'] = ri_dam_df['longitude'].where(ri_dam_df['longitude'] > 0, ri_dam_df['longitude_dem'])

    # same with name, alt name
    ri_dam_df['name'] = ri_dam_df['name'].where(ri_dam_df['name'].isna(), ri_dam_df['dam_name'])
    ri_dam_df['alt_name'] = ri_dam_df['alt_name'].where(ri_dam_df['alt_name'].isna(), ri_dam_df['other__name'])

    # now drop the dem lat / long
    ri_dam_df = ri_dam_df.drop(columns=[
        'latitude_dem',
        'longitude_dem',
        'dam_name',
        'other__name'
    ])

    # ct has encoded their hazards in a frustrating way - let's fix that
    ct_dam_df['dam_haz'] = ct_dam_df['dam_haz'].apply(convert_ct_hazard)

    # load remaining nid data
    ri_nid = pd.read_excel(here("data/NID_RI_U.xlsx"))
    ri_nid = clean_column_names(ri_nid)
    ma_nid = pd.read_excel(here("data/NID_MA_U.xlsx"))
    ma_nid = clean_column_names(ma_nid)
    # reload ct
    ct_nid = pd.read_excel(here("data/NID_CT_U.xlsx"))
    ct_nid = clean_column_names(ct_nid)

    ct_dam_df['owner'] = ct_dam_df['owner'].apply(expand_ct_ownership)

    # at this point it's worth pausing and considering what's in those dataset
    # that were just created. all the GIS data available from the states +
    # NIDs where available + additional DEM data. this makes it possible
    # to join in the AR removed data which uses NID IDs. before that, it's
    # worth cleaning up the columns and renaming the common ones so that
    # joining will result in a cleaner dataset.

    # add state column names
    ri_dam_df['state'] = 'RI'
    ct_dam_df['state'] = 'CT'
    ma_dam_df['state'] = 'MA'

    # rename common columns among the various datasets
    ri_dam_df = ri_dam_df.rename(columns={
        "name": "dam_name",
        "nid": "nid_id",
        "city/town" : "town"
    })

    ct_dam_df = ct_dam_df.rename(columns={
        'nidid' : 'nid_id',
        'dam_haz' : 'hazard'
    })

    ma_dam_df = ma_dam_df.rename(columns={
        'natid' : 'nid_id',
        'damname' : 'dam_name',
        'hazcode' : 'hazard'
    })

    ma_dam_df = ma_dam_df.drop(columns=['damlat', 'damlong'])

    # add removed dam data for RI
    ri_removed_dams = pd.read_csv(here("data/RI Dam removals & fishways.csv"))
    ri_removed_dams = clean_column_names(ri_removed_dams)

    ri_removed_dams = ri_removed_dams[['ri_dam_#', 'action', 'fishway_material', 'other_action', 'type_of_removal']]
    ri_removed_dams['removed'] = np.where(ri_removed_dams['action'] == 'removed', True, False)
    ri_removed_dams['removed'] = np.where(ri_removed_dams['action'] == 'removal ', True, ri_removed_dams['removed'])
    ri_removed_dams = ri_removed_dams.set_index('ri_dam_#')
    ri_dam_df = ri_dam_df.set_index('state_id').join(ri_removed_dams, how='left')
    ri_dam_df.index.name = 'state_id'
    ri_dam_df = ri_dam_df.reset_index()

    # a lot of RI's extra data is simply the data from the NID dataset... and it
    # would be a problem if it was joined and left in. we'll drop the duplicate
    # columns and retain the NID ones.


    ri_dam_df.to_csv(here("results/ri_dams_temp.csv"))
    ma_dam_df.to_csv(here("results/ma_dams_temp.csv"))
    ct_dam_df.to_csv(here("results/ct_dams_temp.csv"))

    # join the datasets
    dam_df = pd.concat([ri_dam_df, ma_dam_df, ct_dam_df], sort=False)

    # add removed dam data for AR
    ar_removed_dams = pd.read_csv(here("data/ARDamRemovalList_Figshare_Feb2020.csv"))
    ar_removed_dams = clean_column_names(ar_removed_dams)

    ar_removed_dams = ar_removed_dams[ar_removed_dams.nid_id.notnull()].set_index('nid_id')
    # get rid of most of the ar columns
    ar_removed_dams = ar_removed_dams[['year_removed']]
    # add 'removed' column
    ar_removed_dams['removed'] = True
    
    dam_df = dam_df.set_index('nid_id').join(ar_removed_dams, how='left', rsuffix='_ar').reset_index()

    # crosswalk ar removed value to other
    dam_df['removed'] = np.where(dam_df['removed_ar'] == True, True, dam_df['removed'])
    dam_df['removed'] = np.where(dam_df['removed'].isna(), False, dam_df['removed'])

    # fix the case of the names - it's a mess
    dam_df['town'] = dam_df['town'].str.title()
    dam_df['dam_name'] = dam_df['dam_name'].str.title()

    # join the NID datasets. this gives us a lot more data, and in some cases
    # fills in the gaps with better names.
    nid_df = pd.concat([ri_nid, ma_nid, ct_nid])

    fin_df = dam_df.set_index('nid_id').join(nid_df.set_index('nidid'), how='left', rsuffix='_nid').reset_index()

    # these columns overlap and now have _nid suffix:
    #    (['dam_name', 'dam_type', 'longitude', 'latitude', 'county', 'purposes',
    #      'hazard', 'outlet_gates', 'state'],

    # copy over missing data names / alt names, then drop from nid
    fin_df['dam_name'] = fin_df['dam_name'].where(fin_df['dam_name'].isna(), fin_df['dam_name_nid'])
    fin_df['alt_name'] = fin_df['alt_name'].where(fin_df['alt_name'].isna(), fin_df['other_dam_name'])
    fin_df['year_completed'] = fin_df['year_completed'].where(fin_df['year_completed'].isna(), fin_df['yr_completed'])
    fin_df['hazard_nid'] = fin_df['hazard_nid'].apply(expand_nid_hazard_names)
    fin_df['hazard'] = fin_df['hazard'].where(fin_df['hazard'].isna(), fin_df['hazard_nid'])
    fin_df['owntype1'] = fin_df['owntype1'].where(fin_df['owntype1'].isna(), fin_df['owner'])

    # drop redundant columns
    fin_df = fin_df.drop(columns=[
        'dam_name_nid',
        'other_dam_name',
        'longitude_nid',
        'latitude_nid',
        'city',
        'hazard_nid',
        'state_nid',
        'yr_completed',
        'owner'
    ])

    # clean up names on remaining columns
    fin_df = fin_df.rename(columns={
        'recordid' : 'nid_recordid',
        'index' : 'nid_id',
        'action' : 'fish_passage_modification',
        'other_action' : 'other_fish_passage_modification'
    })

    # now turn it back into a feature class...
    fin_df.to_csv(here("results/dam_database_temp.csv"), index=False)

    # load it as an XY layer
    dam_db_flayer = "dam_db_flayer"
    arcpy.MakeXYEventLayer_management(
        str(here("results/dam_database_temp.csv")),
        "longitude",
        "latitude",
        dam_db_flayer,
        nad83
    )

    # and stash it in a gdb for later scripts
    output_loc = str(here("results", "results.gdb", "all_raw_dam_data"))
    arcpy.CopyFeatures_management(dam_db_flayer, output_loc)

    # # get the old dam IDs
    # new_dam_to_old_id_map = ea.obj.get_unused_scratch_gdb_obj()
    # original_dam_ids = str(here("data/merged_dam_id.gdb/merged_dams_with_ids"))

    # # perfom identity to get relationships
    # arcpy.Identity_analysis(
    #     output_loc,
    #     original_dam_ids,
    #     new_dam_to_old_id_map,
    #     "ONLY_FID",
    #     "20 Meters",
    #     "NO_RELATIONSHIPS"
    # )

    # # join the nedat_id to the map
    # arcpy.JoinField_management(
    #     new_dam_to_old_id_map,
    #     "FID_merged_dams_with_ids",
    #     original_dam_ids,
    #     ea.table.get_oid_fieldname(original_dam_ids), 
    #     ["NEDAT_ID"]
    # )

    # # now join the nedat_id to the final dataset
    # arcpy.JoinField_management(
    #     output_loc,
    #     ea.table.get_oid_fieldname(output_loc),
    #     new_dam_to_old_id_map,
    #     "FID_merged_dams_v2", 
    #     ["NEDAT_ID"]
    # )

    # finally, make a v2 id

    dam_proj_id = "dam_atlas_id"
    
    oid_fname = "!" + ea.table.get_oid_fieldname(output_loc) + "!"
    
    arcpy.AddField_management(output_loc, dam_proj_id, "LONG")
    arcpy.CalculateField_management(output_loc, dam_proj_id, oid_fname)

    # at this point, we pause: we've combined all the various data sets, never
    # removing anything, and harmonized various columns. we've also added an id.
    # before we split datasets or remove columns, we save a copy for future use.

    complete_df = ea.table.get_arcgis_table_as_df(output_loc)
    complete_df.to_csv(here("results/all_original_dam_data_aggregated.csv"), index=True)