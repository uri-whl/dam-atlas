# -*- coding: utf-8 -*-
"""
Created on 2020-02-08

@author: Josh P. Sawyer
"""

import extarc as ea

import arcpy
from pyprojroot import here

# set environment flags - we don't want Z / M, we do want overwrite on
# the final product
arcpy.env.outputZFlag = "Disabled"
arcpy.env.outputMFlag = "Disabled"
arcpy.env.overwriteOutput = True

arcpy.env.scratchWorkspace = str(here('./results/scratch'))

if __name__ == "__main__":
    ea.logger.setup_logging(here("./src/logging.yaml"))
    ea.logger.send("identifying dam reservoirs")
    
    
    
    
    
    
    ea.logger.send("identification complete")
    