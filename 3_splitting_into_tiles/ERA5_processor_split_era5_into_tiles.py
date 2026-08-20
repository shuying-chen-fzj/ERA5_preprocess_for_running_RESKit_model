# coding: utf-8
# @authors: s-ryberg, s-ishmam, s-chen

from scipy.interpolate import RectBivariateSpline, interp1d
from datetime import datetime, timedelta
from functools import reduce
import numpy as np
import geokit as gk
import shutil
import sys
import os
import netCDF4 as nc
import argparse
VERSION = "0.0.3" # by Shuying, 2024-10-24, added snow variables


def parse_args():
    parser = argparse.ArgumentParser(
        description='Process ERA5 data from raw Global data into yearly files over a given tile and year'
    )
    parser.add_argument('year', type=str, help='Target weather year')
    parser.add_argument('xi',   type=int, help='X-Index of tile')
    parser.add_argument('yi',   type=int, help='Y-Index of tile')
    parser.add_argument('zoom', type=int, help='Zoom level')
    return parser.parse_args()


def clip_era5_data_to_tile(args, ERA5_TOP_DIR):
    """ Clips raw ERA5 data files to the tile defined by args.xi, args.yi, args.zoom for the year args.year
    and deposits them into the appropriate processed directory.
    """
    ## (1) prepare names and directories
    # Set Source
    source_topdir = os.path.join(ERA5_TOP_DIR, "raw")
    source_group = "reanalysis-era5-single-levels"

    # Set Targets
    target_id = f"z{args.zoom}.x{args.xi}.y{args.yi}.y{args.year}"
    target_topdir = os.path.join(ERA5_TOP_DIR, "processed")
    source_year = args.year

    # make target directory structure
    target_dir = target_topdir
    for tmp in [args.zoom, args.xi, args.yi, args.year]:
        target_dir = os.path.join(target_dir, str(tmp))
    if not os.path.isdir(target_dir):
        print("Creating target directory!")
        os.makedirs(target_dir, exist_ok=True)


    ## (2) check if target tiles exist, skip processing if they do
    target_file_variables = [
        # "100m_wind_speed.processed",
        # "100m_wind_direction.processed",
        # "10m_wind_speed.processed",
        # "10m_wind_direction.processed",
        # "boundary_layer_height",
        # "forecast_surface_roughness",
        # "total_sky_direct_solar_radiation_at_surface.processed",
        # "surface_solar_radiation_downwards.processed",
        # "2m_temperature",
        # "2m_dewpoint_temperature",
        # "surface_pressure",
        "snow_albedo",
        "snow_density",
        "snow_depth",
        "snowfall"
    ]
    target_pathlist = []
    for variable in target_file_variables:    
        target_file = f"{source_group}.{target_id}.{variable}.nc"
        target_path = os.path.join(target_dir, target_file)
        target_pathlist.append(target_path)
    for target_path in target_pathlist:
        assert not os.path.isfile(target_path), f"{target_path} \nFile exists! All processing skipped!"


    # (3) start clipping process variable by variable
    # # Write note into processed directory
    # LOG_FILE = "README.md"
    # with open(os.path.join(target_dir, LOG_FILE), 'w') as fo:
    #     fo.write("Begun processing at: " + str(datetime.now()) + "\n")
    #     fo.write("Processor version: " + VERSION + "\n")
    #     fo.write("Desired year: " + source_year + "\n")
    #     fo.write("Zoom level: " + str(args.zoom) + "\n")
    #     fo.write("X-Index: " + str(args.xi) + "\n")
    #     fo.write("Y-Index: " + str(args.yi) + "\n")

    extent_single_levels = gk.Extent.fromTile(args.xi, args.yi, args.zoom).castTo(gk.srs.EPSG4326).pad(2).xXyY
    print("EXTENT:", extent_single_levels)

    # with open(os.path.join(target_dir, LOG_FILE), 'a') as fo:
    #     fo.write("Extent:" + reduce(lambda a,
    #                                 b: f"{a},{b}", extent_single_levels) + "\n")

    def clip_dataset(variable, month=None, target_dir=target_dir, lon_lat_box=extent_single_levels):
        """Clips a netCDF dataset to the spatial domain given by 'lon_lat_box' and deposits it into 'target_dir'"""

        source_name = f"{source_group}.{source_year}.{variable}.nc"
        print("  ", source_name)
        source = os.path.join(source_topdir, source_year, source_name)

        target_name = f"{source_group}.{target_id}.{variable}.nc"
        target = os.path.join(target_dir, target_name)

        r = os.system(
            f"cdo sellonlatbox,{lon_lat_box[0]},{lon_lat_box[1]},{lon_lat_box[2]},{lon_lat_box[3]} {source} {target}")
        if not r == 0:
            raise RuntimeError("File Clipping Failed:", variable, month)


    source_variables = [
        # VARIABLE NAME                                ,
        ### "friction_velocity",
        # "100m_v_component_of_wind",
        # "100m_u_component_of_wind",
        # "10m_u_component_of_wind",
        # "10m_v_component_of_wind",
        # "boundary_layer_height",
        # "forecast_surface_roughness",
        # "total_sky_direct_solar_radiation_at_surface",
        # "surface_solar_radiation_downwards",
        # "2m_temperature",
        # "2m_dewpoint_temperature",
        # "surface_pressure",
        "snow_albedo",
        "snow_density",
        "snow_depth",
        "snowfall"
    ]
    for variable in source_variables:
        print("CLIPPING:", variable)
        clip_dataset(variable)


def main_func():
    # input tiles and year information
    args = parse_args()

    # Clip raw ERA5 data files
    '''
    In order to run the following function, please make sure to set the correct path for ERA5_TOP_DIR variable, and make sure you have a working environment with cdo.
    1. ERA5_TOP_DIR: The top directory where the ERA5 data is stored.
    2. The raw ERA5 data directory structure under ERA5_TOP_DIR should be mannually organized as follows:
        ERA5_TOP_DIR/raw/{year}/reanalysis-era5-single-levels.{year}.{variable}.nc
    3. The processed data will be automatically stored under:
        ERA5_TOP_DIR/processed/{zoom}/{xi}/{yi}/{year}/reanalysis-era5-single-levels.z{zoom}.x{xi}.y{yi}.y{year}.{variable}.nc
    4. Run the script with the appropriate arguments for year, xi, yi, and zoom level. For example:
        python ERA5_processor_tile_for_direct_vars.py 2020 10 15 4
        This will process the ERA5 data for the year 2020 for the tile defined by x-index 10, y-index 15 at zoom level 4.
    '''
    ERA5_TOP_DIR = "/fast/central/projects/2021_s-chen_PhD/projects_root/0018_explore_snow_data/era5_snow/global"
    clip_era5_data_to_tile(args=args, ERA5_TOP_DIR=ERA5_TOP_DIR)


if __name__ == "__main__":
    main_func()
    