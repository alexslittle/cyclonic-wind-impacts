#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# --------------------------------------------------------------------------------

# Built-in modules
from pathlib import Path

# conda-installed modules
import numpy as np
import xarray as xr
from tqdm import tqdm

# Side modules
import footprints
from lib import *
from params import *
import ssi

experiments = ["historical",
               "ssp245",
               "ssp585"]

models = ["ACCESS-CM2",
          "BCC-CSM2-MR",
          "EC-Earth3",
          "ERA5",
          "KIOST-ESM",
          "MIROC6",
          "MPI-ESM1-2-HR",
          "MPI-ESM1-2-LR",
          "MRI-ESM2-0"]

# Construct 1-D vectors containing lat and lon grid-points
lat_vector = build_vector(south_bound, north_bound, resolution)
lon_vector = build_vector(west_bound, east_bound, resolution)

# Construct 2-D grid covering domain
lat_grid, lon_grid = np.mgrid[south_bound: north_bound + resolution: resolution,
                              west_bound: east_bound + resolution: resolution]


def main():

    # Loop through experiments
    for exp in tqdm(sorted(experiments),
                    total=len(experiments),
                    position=1,
                    leave=False,
                    desc="EXPERIMENT",
                    colour="magenta",
                    ):

        pop = xr.open_dataset(
                filename_or_obj=Path(
                    f"./cyclonic-wind-impacts/data/population/population_{exp}.nc"
                )
            )

        # Loop through CMIP6 models and ERA5 reanalysis
        for model in tqdm(sorted(models),
                          total=len(models),
                          position=2,
                          leave=False,
                          desc="MODEL     ",
                          colour="red",
                          ):

            # Only historical data exists for ERA5
            if exp == "historical" or model != "ERA5":

                # Read wind field data for the experiment/model combo
                wind_field = xr.open_dataset(
                    filename_or_obj=Path(
                        f"./cyclonic-wind-impacts/data/sfcWind/{exp}/sfcWind_{exp}_{model}.nc",
                    )
                )

                # Generate cyclone footprints
                footprints.main(exp,
                                model,
                                lat_vector,
                                lon_vector,
                                lat_grid,
                                lon_grid,
                                wind_field,
                                )

                # Generate SSI results
                # ssi.main(exp,
                #          model,
                #          wind_field,
                #          pop,
                #          )
            else:
                pass


if __name__ == "__main__":
    main()
