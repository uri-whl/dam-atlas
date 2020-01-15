# Dam Atlas Project

This repository scripts and source data (where size is reasonable) for generating the data used in the Dam Atlas project. Due to the nature of programmatically working with geospatial data, this is a collection of scripts.

## Overview

## Installation

These scripts utilize `arcpy` from ArcGIS Pro (i.e., the 64 bit python 3 binary - though they may be backwards compatible with ArcGIS Desktop 32-bit python 2). ArcGIS Pro ships with Conda pre-installed which allows you to create an environment specific for a project without destroying your base environment. If you'd like to set up a project specific environment, you can do the following:

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
        dam-atlas> conda install -c conda-forge pyprojroot
        ```

## Running

The only caveat with this project is that some scripts depend on the output of other scripts. You must first run, in order:

1. `aggregate_harmonize_dam_data.py`
2. `snap_dam_to_nhdplushr.py`

At this point, you will have:

- A shapefile containing all harmonized attribute data, snapped where possible to NHDPlus HR, with a column indicating whether snapping was successful, `all_dams_harmonized`
- A shapefile containing the attribute data and points for only those dams which were succesfully snapped, `all_dams_snapped`

Every subsequent script builds upon `all_dams_snapped`, using the unique ID to generate either associated polygon data or additional attribute data.

When ready to load data into MapBox, run the final script `build_geojson_data.py` which will join all attribute data together (where appropriate) and generate GeoJSON data for the dams. Additionally, you will want to run:

- `build_geojson_hydro.py` to build HUC, waterbody and hydroline GeoJSON files
- `build_geojson_dam_wsheds.py` to build the GeoJSON corresponding to the delineated watersheds for the dams


## Contents

- `data` - Source data for the dams collected from state websites. Large datasets which are easily obtained are not included - specifically:
  - NHD Plus HR Vector Datasets, all downloadable from [The National Map](https://viewer.nationalmap.gov/basic/). The ones used for this are all 4 digit HUCs beginning 01 to cover the bulk of New England.

- `doc`
- `results` - This folder contains the output of the scripts located in `src`, _when the size is reasonable_. For instance, a file geodatabase containing NHDPlus HR products is not included - but a GeoJSON file describing dams would be.
- `src` - The scripts which generate additional dam data. Specifically:

    - `aggregate_harmonize_dam_data.py` combines the source dam data and assigns a state column, then harmonizes the remaining column based on rules derived from the metadata in `doc/`.
    - `snap_dam_to_nhdplushr.py` aligns dam points (with arcpy `Snap`) to NHD Plus HR, generating lat / long values and a column describing whether it snapped. it then recalculates the hucs - 2-digit through 12-digit for the new locations.

## References

1. Franey, T. (2018). Exploring New England Dams Analysis Using the High Resolution National Hydrography Dataset [MESM Major Paper, University of Rhode Island]. <http://www.edc.uri.edu/mesm/Docs/MajorPapers/Franey_2018.pdf>
2. Gold, A., Addy, K., Morrison, A., & Simpson, M. (2016). Will Dam Removal Increase Nitrogen Flux to Estuaries? Water, 8(11), 522. <https://doi.org/10.3390/w8110522>
