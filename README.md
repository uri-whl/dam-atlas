# New England Dam Atlas

This repository contains scripts and source data (where size is reasonable) for generating the data used in the Dam Atlas project.

## Overview

In aggregate, this project combines data on dams from multiple states (RI, CT, MA), aligns it to an established flow network (NHDPlus High Resolution), discards any dams that cannot be aligned or are not in the target area and runs various calculations to bring in additional information.

The goal of this project is to script the creation of various GeoJSON datasets for use in a Mapbox website and eliminate some of the noise within the datasets.

## Installation

### Setting up the code environment

These scripts utilize `arcpy` from ArcGIS Pro (i.e., the 64 bit python 3 binary - though they may be backwards compatible with ArcGIS Desktop 32-bit python 2). ArcGIS Pro ships with Conda pre-installed which allows you to create an environment specific for a project without destroying your base environment. If you'd like to set up a project specific environment, you can do the following (If you have admin rights on your machine, you can install the packages to the base environment):

1. In Start Menu, navigate to `ArcGIS > Python Command Prompt`, _not_ `Python (Command Line)`. You'll know if you got the right one because you'll see:

    ```bash
    (arcgispro-py3) C:\Program Files\ArcGIS\Pro\bin\Python\envs\arcgispro-py3>
    ```

2. To clone an environment, type:

    ```bash
    > conda create --name dam-atlas --clone arcgispro-py3
    ```

    where `dam-atlas` can be whatever name you like. Wait for this action to complete.

3. From within ArcGIS Pro, click `Project`, then `Python` then `Manage Enviroments`. Set `dam-atlas` to active. Close ArcGIS Pro and the `Python Command Prompt` window. Your new environment is set.

4. You can now install additional packages:
    1. Thought you can install packages from within ArcGIS Pro, it seems to get hung up, as conda actually prompts you to proceed. Re-open the `Python Command Prompt` - you'll be in the `dam-atlas` environment.

    2. We recommend Spyder as an IDE. Type:

        ```bash
        dam-atlas> conda install spyder
        ```

       and then 'y' when prompted to proceed. Various packages will be downloaded and updated to 'solve' the environment - i.e., choose versions of packages which will actually work with eachother. You'll be returned to the command prompt when finished.

    3. You must install the following packages as well (commands included - sometimes on different channels):

        ```bash
        dam-atlas> pip install pyhere=1.0.0
        dam-atlas> pip install extarc=0.0.1
        dam-atlas> conda install pyyaml
        ```

    4. Optionally, if you want to use the mapbox CLI, you need to install their module, `mapbox-tilesets`

        ```bash
        dam-atlas> pip install mapbox-tilesets
        ```

        See [Mapbox Data Creation](doc/mapbox_data_creation.md).

### Setting up data that's not included in this repository

NHDPlus HR data is not included in this repository for size reasons. 

## Running

The only caveat with this project is that some scripts depend on the output of other scripts. You must first run, in order:

1. `00_aggregate_harmonize_dam_data.py` - combines all the filtered datasets into one dataset and crosswalks the attributes to common names.
2. `02_snap_dam_to_nhdplushr.py` - snaps all the dams to NHD flowlines for HUC 01*
3. `03_cut_dam_dataset_to_ri.py` - eliminates all the dams that either don't drain into a RI watershed and aren't within the RI boundary. if either condition is true, the dam is retained.

At this point, you will have:

- Two feature classes containing harmonized attribute data - one of snapped dams,
  and one of dams that couldn't snap. These feature classes are located in:
  - 1
  - 2

## Contents

- `data` - Source data for the dams collected from state websites. Large datasets which are easily obtained are not included - specifically:
  - NHD Plus HR Vector Datasets, all downloadable from [The National Map](https://viewer.nationalmap.gov/basic/). The ones used for this are all 4 digit HUCs beginning 01 to cover the bulk of New England.

- `doc`
- `src` - The scripts which generate additional dam data. Specifically:
  - `00_aggregate_harmonize_dam_data` crosswalks the RI / CT / MA data and joins it to NID data and American Rivers data.
  - `02_snap_dam_to_nhdplushr.py` aligns dam points (with arcpy `Snap`) to NHD Plus HR, generating lat / long values, and two datasets - one with snapped dams, one without.
  - `03_associated_dams_with_huc12.py` associates snapped dams (really, any point feature class) with NHD HUCs.
  - `04_cut_dam_dataset_to_ri.py` reduces the dam set further to only those dams within the RI state boundary and within watersheds which drain in RI. Note: this is a slight problem, as dams in western / eastern RI may drain to different watersheds outside of the state, but the full collection of dams within that watershed have not been retained. As such, any watershed-spanning metrics (i.e., ecological metrics around functional networks) will be erroneous for those dams.
  - `50_build_geojson_files.py`
  - `nhd_to_geojson.py` takes nhd flowlines, hucs and water bodies and converts them to geojson files for use within mapbox.
  - `nhd_geojson_to_mapbox` is a bash script that adds geojson as sources to mapbox and then creates tilesets from the recipes in `results/mapbox-recipes`. It needs a real access token and probably a new ID to run.
  - `identify_dam_reservoirs.py` follows the guidelines in Franey 2018 & Gold et al. 2016 for identifying reservoirs of dams based on proximity. Note: it doesn't differentiate between upstream or downstream reservoirs, so visual inspection is required.
- `results` - This folder contains the output of the scripts located in `src`, _when the size is reasonable_. For instance, a file geodatabase containing NHDPlus HR products is not included - but a GeoJSON file describing dams might be.
  - `geojson` contains data in GeoJSON format for use with Mapbox. The only file that's actually is the GeoJSON file for the dams - NHD files are too large and must be generated via `nhd_to_geojson.py`.
  - `mapbox-recipes` contains the recipes used to create tilesets within mapbox.

## References

1. Franey, T. (2018). Exploring New England Dams Analysis Using the High Resolution National Hydrography Dataset [MESM Major Paper, University of Rhode Island]. <http://www.edc.uri.edu/mesm/Docs/MajorPapers/Franey_2018.pdf>
2. Gold, A., Addy, K., Morrison, A., & Simpson, M. (2016). Will Dam Removal Increase Nitrogen Flux to Estuaries? Water, 8(11), 522. <https://doi.org/10.3390/w8110522>
