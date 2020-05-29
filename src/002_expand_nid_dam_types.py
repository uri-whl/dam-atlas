# -*- coding: utf-8 -*-
"""
Created on 5/25/2020

Takes NID dam type abbreviations and expands them to full text, then convers
upper case to title case.

@author: Josh P. Sawyer
"""

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

def remap_nid_dam_types(x):
    """
    These values are coming from nid.sec.usace.army.mil/ on the Help page

    Code	Value
    RE	Earth
    ER	Rockfill
    PG	Gravity
    CB	Buttress
    VA	Arch
    MV	Multi-Arch
    CN	Concrete
    MS	Masonry
    ST	Stone
    TC	Timber Crib
    OT	Other
    RC	RCC
    """
    # the NID data has non-delimited values, e.g. CNMSRE, but they're all length
    # two so we can explode them as follows:

    types = (x[0+i:2+i] for i in range(0, len(x), 2))

    # if we had 'CNMSRE' we now have ['CN', 'MS', 'RE']
    # now iterate over and convert to their expanded names and append them
    # to a comma delimited string

    new_string = ""

    type_dict = {
        "RE": "Earth",
        "ER": "Rockfill",
        "PG": "Gravity",
        "CB": "Buttress",
        "VA": "Arch",
        "MV": "Multi-Arch",
        "CN": "Concrete",
        "MS": "Masonry",
        "ST": "Stone",
        "TC": "Timber Crib",
        "OT": "Other",
        "RC": "RCC",
    }

    for type in types:
        # if we can find the type in the dictionary, we add it
        try:
            new_string += type_dict[type]
        except KeyError:
            new_string += "Unknown"
        #add delimiter
        new_string+=","

    # remove final comma
    new_string = new_string[:-1]

    return new_string


if __name__ == "__main__":
    ea.logger.setup_logging(here("src", "logging.yaml"))
    logger = logging.getLogger(__name__)
    
    logger.info("expanding NID dam type to full text")

    dam_df = pd.read_csv(here("results/all_original_dam_data_aggregated.csv"))

    # dam_atlas_id is our unique key, and the columns we're interested in
    # are 'dam_type' and 'dam_type_nid'

    # practically speaking, 'dam_type' is almost exactly the same as 'dam_type_nid'
    # except where RI DEM has done some additional exploratory work, so we want
    # to expand 'dam_type_nid' to full text, copy it to 'dam_type' and then
    # convert it to Title Case to make it a little easier on the eyes.

    # anyway, drop all other columns:

    dam_df = dam_df[['dam_atlas_id', 'dam_type', 'dam_type_nid']]

    # apply a remapping function
    dam_df['dam_type_nid'] = dam_df['dam_type_nid'].fillna("").apply(remap_nid_dam_types)

    # replace values with NID where NID exists

    dam_df['dam_type_correct'] = dam_df['dam_type'].where(~dam_df['dam_type'].isna(), dam_df['dam_type_nid'])

    # title case - get rid of lingering NA, too
    dam_df['dam_type_correct'] = dam_df['dam_type_correct'].fillna("").str.title()

    # reassign columns and drop extra
    dam_df['dam_type'] = dam_df['dam_type_correct']
    dam_df = dam_df[['dam_atlas_id', 'dam_type']]
