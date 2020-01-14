# Dam Atlas Project

This repository scripts and source data (where size is reasonable) for generating the data used in the Dam Atlas project. Due to the nature of programmatically working with geospatial data, this is a collection of scripts.

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

4. _(Optional)_ You can now install additional packages.
   a. Thought you can install packages from within ArcGIS Pro, it seems to get hung up, as conda actually prompts you to proceed. Re-open the `Python Command Prompt` - you'll be in the `dam-atlas` environment.

   b. We recommend Spyder as an IDE. Type:

    ```bash
    dam-atlas>conda install spyder
    ```

    and then 'y' when prompted to proceed. Various packages will be downloaded and updated to 'solve' the environment - i.e., choose versions of packages which will actually work with eachother. You'll be returned to the command prompt when finished.

   c. Open up Spyder and proceed as usual.

## Contents

- `data` - Source data for the dams collected from state websites. Large datasets which are easily obtained are not included - specifically:

    - NHD Plus HR Vector Datasets, all downloadable from [The National Map](https://viewer.nationalmap.gov/basic/). The ones used for this are all 4 digit HUCs beginning 01 to cover the bulk of New England.

- `doc`
- `results` - This folder contains the output of the scripts located in `src`, _when the size is reasonable_. For instance, a file geodatabase containing NHDPlus HR products is not included - but a GeoJSON file describing dams would be.
- `src` - The scripts which generate additional dam data. Specifically:

    - `aggregate_harmonize_dam_data.py` is an R notebook for harmonizing the columns of the various state sources using the attribute metadata descriptions in `doc`.
    - `snap_dam_to_nhdplushr.py` is a Python script utilizing `arcpy` to align dam coordinates to NHD Plus HR.

## References

- Franey, T. (2018). Exploring New England Dams Analysis Using the High Resolution National Hydrography Dataset [MESM Major Paper]. University of Rhode Island.
- Gold, A., Addy, K., Morrison, A., & Simpson, M. (2016). Will Dam Removal Increase Nitrogen Flux to Estuaries? Water, 8(11), 522. https://doi.org/10.3390/w8110522
