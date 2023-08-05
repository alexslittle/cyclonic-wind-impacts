#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@File    :   generate_ssis.py
@Date    :   2022/06/04
@Author  :   Alex Little
@Desc    :   Calculate storm severity indices for individual cyclone tracks
"""

# --------------------------------------------------------------------------------

# Built-in modules
import math
from pathlib import Path

# PyPI packages
import xarray as xr
from tqdm import tqdm

# Side modules
from base_funcs import _extreme_winds
from params import *

# Loop through experiments
for experiment in tqdm(sorted(experiments),
                       total=len(experiments),
                       position=1,
                       leave=False,
                       desc="EXPERIMENT",
                       colour="magenta",
                       ):

    # Read population data for the given experiment
    population = xr.open_dataset(
        filename_or_obj=Path(
            f"./data/population/population_{experiment}.nc",
        )
    )

    # Loop through CMIP6 models and ERA5 reanalysis
    for model in tqdm(sorted(models),
                      total=len(models),
                      position=2,
                      leave=False,
                      desc="MODEL",
                      colour="red",
                      ):

        # Only historical data exists for ERA5
        if experiment != "historical" and model == "ERA5":
            pass

        else:
            # Read wind field data for the given experiment and model
            wind_field = xr.open_dataset(
                filename_or_obj=Path(
                    f"./data/sfcWind/{experiment}/sfcWind_{experiment}_{model}.nc",
                )
            )

            # Get extreme wind climatology field used to calculate SSI
            adjusted_extremes = _extreme_winds(wind_field, impact_threshold)

            # List individual footprint files (ignore hidden files)
            footprint_files = [f for f in Path(f"./outputs/footprints/{experiment}/{model}").iterdir()
                               if not f.name.startswith(".")]

            # Create subdirectory to contain output footprints
            subdir = Path(f"./outputs/ssis/{experiment}/{model}/")
            subdir.mkdir(parents=True, exist_ok=True)

            # Initialise accumulated loss
            accumulated_loss = 0

            for path in tqdm(sorted(footprint_files),
                             total=len(footprint_files),
                             leave=False,
                             desc="SSI",
                             colour="white",
                             ):

                # Get maximum wind speeds across domain attributable to the cyclone over its lifetime
                footprint = xr.open_dataset(path)
                footprint_max = footprint.max(dim="time")

                # Mask footprint where wind speeds are less than the impact threshold or local climatological extreme
                exceedance_footprint = footprint_max.where(
                    footprint_max >= adjusted_extremes, other=math.nan
                )

                # Calculate storm severity index (unweighted)
                ssi = (((exceedance_footprint / adjusted_extremes) - 1) ** 3).rename(
                    {"sfcWind": "ssi"},
                ).drop_vars(
                    "quantile",
                )

                # Calculate population-weighted storm severity index and assign to dataset
                ssi.assign(ssiPop=ssi.ssi * population.population).to_netcdf(
                    f"{subdir}/ssi_{path.name[path.name.find('_'):][1:]}"
                )
