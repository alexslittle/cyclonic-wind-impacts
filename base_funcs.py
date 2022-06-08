#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@File    :   base_funcs.py
@Date    :   2022-06-08
@Author  :   Alex Little
@Desc    :   Base functions used to calculate wind footprints and SSIs.
"""

# --------------------------------------------------------------------------------

# Built-in modules
from calendar import isleap
import re
from typing import Tuple

# PyPI packages
import numpy as np
import pandas as pd
import xarray as xr

# Suppress SettingWithCopy warnings.
pd.options.mode.chained_assignment = None


def _start_year(filename: str) -> int:
    """
    Get the start year of winter for a given track file.
    """
    # Get the first substring in each filename containing 8 consecutive digits
    substring = re.findall(r"(\d{8})", filename)[0]

    # Extract the start year (first 4 digits in substring) and convert to int
    return int(substring[0:4])


def _season_range(year: int,
                  leap_days: bool) -> pd.DatetimeIndex:
    """
    Generate time series for a given winter.
    """
    # Number of days in Feb depends on whether next year is leap or not
    days_in_feb = 29 if leap_days and isleap(year + 1) else 28

    # Number of days in winter (always 62 days in Dec and Jan)
    day_count = 62 + days_in_feb

    # Produce time series for season with delta period intervals
    return pd.date_range(start=np.datetime64(f"{year}-12-01T00"),  # Start of winter is 1st December, midnight
                         periods=day_count * 4,  # 4 track points per day
                         freq="6H")


def _track_indices(track_index: int,
                   split_at_rows: list,
                   ) -> Tuple[int, int]:
    """
    Get the track row index values at which to slice rows within text file.
    """
    start_index = split_at_rows[track_index] + 2  # Omit the first two rows of data for each track (unneeded info)
    end_index = split_at_rows[track_index + 1]
    return start_index, end_index


def _circle_mask(lat_centre: float,
                 lon_centre: float,
                 lat_grid: np.ndarray,
                 lon_grid: np.ndarray,
                 radius: float,
                 resolution: float,
                 ) -> np.ndarray:
    """
    Create a circular mask centred at given geographical coordinates.
    """
    # Calculate radius of circle on the grid
    grid_radius = radius / resolution

    # Calculate distance of each point from the circle centre
    dist_from_centre = np.sqrt((lat_grid - lat_centre) ** 2 + (lon_grid - lon_centre) ** 2)

    # Mask all points outside the circle
    return dist_from_centre <= grid_radius


def _shift_time(time: pd.DatetimeIndex,
                period: int,
                ) -> Tuple[pd.DatetimeIndex, pd.DatetimeIndex]:
    """
    Shift a time in both directions by a given period.
    """
    # Create timedelta based on period
    shift = np.timedelta64(period, "h")

    # Calculate time bounds before and ahead of central time
    return time - shift, time + shift


def _extreme_winds(wind_field: xr.Dataset,
                   impact_threshold: float,
                   ) -> xr.Dataset:
    """
    Get the extreme wind climatology above a given impact threshold.
    """

    # Calculate the extreme winter wind distribution (98th percentile)
    extreme_winds = wind_field.quantile(
        q=0.98, dim="time",
    )

    # Set the impact threshold as the minimum extreme wind speed (ignore masked values)
    return extreme_winds.where(
        (extreme_winds.sfcWind >= impact_threshold) | (extreme_winds.isnull()), other=impact_threshold,
    )
