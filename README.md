# Dam Atlas Project

This repository scripts and source data (where size is reasonable) for generating the data used in the Dam Atlas project. Due to the nature of programmatically working with geospatial data, this is a collection of scripts.

## Contents

- `data` - Source data for the dams collected from state websites. Large datasets which are easily obtained are not included - specifically:

    - NHD Plus HR Vector Datasets, all downloadable from [The National Map](https://viewer.nationalmap.gov/basic/). The ones used for this are all 4 digit HUCs beginning 01 to cover the bulk of New England.

- `doc`
- `results` - This folder contains the output of the scripts located in `src`, _when the size is reasonable_. For instance, a file geodatabase containing NHDPlus HR products is not included - but a GeoJSON file describing dams would be.
- `src` - The scripts which generate additional dam data. Specifically:

    - `mung_dam_columns.Rnb` is an R notebook for harmonizing the columns of the various state sources using the attribute metadata descriptions in `doc`.
    - `snap_dam_to_nhdplushr.py` is a Python script utilizing `arcpy` to align dam coordinates to NHD Plus HR.

## References

Franey, T. (2018). Exploring New England Dams Analysis Using the High Resolution National Hydrography Dataset [MESM Major Paper]. University of Rhode Island.
Gold, A., Addy, K., Morrison, A., & Simpson, M. (2016). Will Dam Removal Increase Nitrogen Flux to Estuaries? Water, 8(11), 522. https://doi.org/10.3390/w8110522
