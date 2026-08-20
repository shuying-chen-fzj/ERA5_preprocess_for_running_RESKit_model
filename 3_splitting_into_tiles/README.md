information, documented by s.chen@fz-juelich.de on 2025-08-21

**To split ERA5 data set into tiles**

# why this is important?
In order to run the RESKit model using ERA5 data, the splitting process is not necessary. But when your study area is a large area like global and when you have thousands of placements to be calculated, the weather data reading part will feel like forever. By splitting the ERA5 data into tiles, RESKit could locate percisely the placements to a certain tile and read the associated tile only for these placements. This would save lots of weather data reading time compared to ERA5 data without splitting.

# how to split ERA5 data set into tiles
0. This procedure was initially created by s-ryberg and s-ishmam, and updated by s-chen. Original location of files are at [jugit](https://jugit.fz-juelich.de/iek-3/groups/global-systems/ishmam/weather_data_processing/-/tree/master?ref_type=heads).

1. In order to clip raw ERA5 data into tiles, please make sure to set the correct path for ERA5_TOP_DIR variable at the python file 'ERA5_processor_split_era5_into_tiles.py', and make sure you have a working environment with cdo. As documented inside the python file and here:
    1. ERA5_TOP_DIR: The top directory where the ERA5 data is stored.
    2. The raw ERA5 data directory structure under ERA5_TOP_DIR should be mannually organized as follows:
        ERA5_TOP_DIR/raw/{year}/reanalysis-era5-single-levels.{year}.{variable}.nc
    3. The processed data will be automatically stored under:
        ERA5_TOP_DIR/processed/{zoom}/{xi}/{yi}/{year}/reanalysis-era5-single-levels.z{zoom}.x{xi}.y{yi}.y{year}.{variable}.nc
    4. Run the script with the appropriate arguments for year, xi, yi, and zoom level. For example:
        ```python
        python ERA5_processor_split_era5_into_tiles.py 2020 10 15 4
        ```
        This will process the ERA5 data for the year 2020 for the tile defined by x-index 10, y-index 15 at zoom level 4.
    5. One can also run the script using calculation resource management system slurm. Examples are given under the submit folder to get (1) all the global tiles at zoom_level=4, (2) get one specific tile
