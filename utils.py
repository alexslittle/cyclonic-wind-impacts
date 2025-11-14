#!/usr/bin/env python3
# -*- coding: utf-8 -*-

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
    Get the start year of the winter season for a given track file.

    Args:
        filename: The name of the track file for which to obtain the start year.

    Returns:
        The start year of the winter season for the given track file.
    """
    # Get the first substring in each filename containing 8 consecutive digits
    substring = re.findall(r"(\d{8})", filename)[0]

    # Extract the start year (first 4 digits in substring) and convert to int
    return int(substring[0:4])


def _season_range(year: int, include_leap_days: bool) -> pd.DatetimeIndex:
    """
    Generate a 6-hourly time series for a given winter season.

    Args:
        year: The start year of the winter season.
        include_leap_days: Flag to include leap days (29 Feb) in the time series.

    Returns:
        A time series from December to February (inclusive) with 6-hourly intervals.
    """
    # Number of days in Feb depends on whether next year is leap or not
    days_in_feb = 29 if include_leap_days and isleap(year + 1) else 28

    # Number of days in winter (always 62 days in Dec and Jan)
    day_count = 62 + days_in_feb

    # Produce time series for season with delta period intervals
    return pd.date_range(
        start=np.datetime64(f"{year}-12-01T00"),  # Start of winter season is 1st December, midnight
        periods=day_count * 4,  # 4 track points per day
        freq="6H"
    )


def _track_indices(track_index: int, split_at_rows: list) -> Tuple[int, int]:
    """
    Get the track row index values at which to slice rows within a text file.

    Args:
        track_index: The index of the specific track to slice within the text file.
        split_at_rows: All row indices seperating tracks within the text file.

    Returns:
        The row indices seperating the specific track within the text file.
    """
    start_index = split_at_rows[track_index] + 2  # Omit the first two rows of data for each track (unneeded info)
    end_index = split_at_rows[track_index + 1]
    return start_index, end_index


def _circle_mask(lat_centre: float, lon_centre: float, lat_grid: np.ndarray, lon_grid: np.ndarray, radius: float) -> np.ndarray:
    """
    Create a circular mask centred at given geographical coordinates.

    Args:
        lat_centre: The latitude of the circle's centre (units: decimal degs).
        lon_centre: The longitude of the circle's centre (units: decimal degs).
        lat_grid: 2-D latitude grid.
        lon_grid: 2-D longitude grid.
        radius: The radius of the circle (units: decimal degs).
    
    Returns:
        A 2-D array where points outside the specified circle are masked.
    """
    # Calculate distance of each point from the circle centre
    dist_from_centre = np.sqrt((lat_grid - lat_centre) ** 2 + (lon_grid - lon_centre) ** 2)

    # Mask all points outside the circle
    return dist_from_centre <= radius


def _shift_time(time: pd.DatetimeIndex, period: int) -> Tuple[pd.DatetimeIndex, pd.DatetimeIndex]:
    """
    Shift a time in both directions by a given period.

    Args:
        time: A given date and time, e.g. '2025-12-01 00:00:00'.
        period: The number of hours by which to shift the time.
    
    Returns:
        A tuple containing new times after shifting by the number of periods, both before and ahead. 
    """
    # Create timedelta based on period
    shift = np.timedelta64(period, "h")

    # Calculate time bounds before and ahead of central time
    return time - shift, time + shift


def _extreme_winds(wind_field: xr.Dataset, impact_threshold: float) -> xr.Dataset:
    """
    Get the extreme wind climatology above a given impact threshold.

    Args:
        wind_field: A dataset containing all wind speeds across the 2-D domain.
        impact_threshold: The surface wind speed above which impacts occur (units: m/s).
    
    Returns:
        A dataset where wind speeds are clipped to the given minimum value of impact threshold.
    """
    # Calculate the extreme winter wind distribution (98th percentile)
    extreme_winds = wind_field.quantile(q=0.98, dim="time")

    # Set the impact threshold as the minimum extreme wind speed (ignore masked values)
    return extreme_winds.where(
        (extreme_winds.sfcWind >= impact_threshold) | (extreme_winds.isnull()), other=impact_threshold,
    )
