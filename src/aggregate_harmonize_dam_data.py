# -*- coding: utf-8 -*-
"""
Created on Tue Jan 14 15:20:42 2020

@author: Josh
"""

import arcpy
from pyprojroot import here
from arcutils import arcutils as au
from arcutils.common_logger import setup_logging
import logging

import pandas as pd

if __name__ == "__main__":
    # create a logger
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("Aggregating dam data to common file")

    wgs84 = au.get_sr_wgs84()