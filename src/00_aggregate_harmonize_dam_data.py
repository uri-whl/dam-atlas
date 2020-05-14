# -*- coding: utf-8 -*-
"""
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

arcpy.env.scratchWorkspace = str(here("results", "scratch"))

if __name__ == "__main__":
    ea.logger.setup_logging(here("src", "logging.yaml"))
    logger = logging.getLogger(__name__)
    
    logger.info("Aggregating dam data to common file started")

    # NID data and NHD data are in NAD83 - make them all match when projecting
    nad83 = ea.sr.get_sr_nad83_gcs()

    # these dams are the only feature classes - reproject to nad83
    ri_dams = here()
    ct_dams = here()
    ma_dams = here()

    # add x / y coordinates for the reprojected data

    # load the attribute tables of the reprojected data as dataframes

    # ct doesn't have an NID attribute - perform a spatial join to get a relationship
    # table so that they can be joined together

    # load the remaining data as dataframes
    ri_dams_dem = here()

    ri_removed_dams = here()
    ar_removed_dams = here()

    ri_nid = here()
    ct_nid = here()
    ma_nid = here()

    # join ct to ct->nid map

    # join ri DEM data to ri RIGIS data


    # sanitize the column names

    # df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('(', '').str.replace(')', '')

    #
    # at this point it's worth pausing and considering what's in those dataset
    # that were just created. all the GIS data available from the states +
    # NIDs where available + additional DEM data. this makes it possible
    # to join in the AR removed data which uses NID IDs. before that, it's
    # worth cleaning up the columns and renaming the common ones so that
    # joining will result in a cleaner dataset.
    #

    # remove garbage columns - there are a lot

    # rename common columns among

    # add removed dam data for RI

    # add removed dam data for AR

    # add 'removed' column based on the removal data - this allows
    # quick splitting of dam datasets.

    # join the NID datasets. this gives us a lot more data, and in some cases
    # fills in the gaps with better names.

