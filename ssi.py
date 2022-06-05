#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@File    :   ssi.py
@Date    :   2022/06/04
@Author  :   Alex Little
@Desc    :   Calculate storm severity indices for individual cyclone tracks
"""

# --------------------------------------------------------------------------------

# Built-in modules
from pathlib import Path

# conda-installed modules
import xarray as xr
from tqdm import tqdm

# Side modules
from params import *


def main(experiment: str,
         model: str,
         wind_field: xr.Dataset,
         pop: xr.Dataset,
         ):

    # Calculate the extreme winter wind distribution (98th percentile)
    extreme_winds = wind_field.quantile(
        q=0.98, dim="time",
    )

    # Raise all extreme values below the impact threshold up to the value of the threshold
    adjusted_threshold = extreme_winds.where(
        extreme_winds.sfcWind >= impact_threshold, other=impact_threshold
    )

    # List individual footprint files (ignore hidden files)
    footprint_files = [f for f in Path(f"./cyclonic-wind-impacts/footprints/{experiment}/{model}").iterdir()
                       if not f.name.startswith(".")]

    # Calculate the footprint
    accumulated_loss = 0
    for footprint in tqdm(sorted(footprint_files),
                          total=len(footprint_files),
                          leave=False,
                          desc="SSI",
                          colour="white",
                          ):

        ssi = ((footprint.sfcWind.max(dim="time") / adjusted_threshold.sfcWind) - 1) ** 3
        ssi_population_weighted = ssi * pop.population
        accumulated_loss += ssi_population_weighted.sum()

        print(ssi_population_weighted)
    print(accumulated_loss)
