#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Built-in libs.
import re

# Standard libs.
import numpy as np
import pandas as pd


def is_leap_year(year,
                 ):
    """
    Checks to see if a given year is a leap year, and returns the result.

    Arguments:
    ---------------------------------------------------------------------------
    year (int) -- :

    Returns:
    ---------------------------------------------------------------------------
    A boolean value describing whether or not the input year is a leap year.
    """
    # If a year is divisible by 100 and 400, it is a leap year.
    century_cond = (year % 400 == 0) & (year % 100 == 0)

    # If a year is divisible by 4 but not 100, it is also a leap year.
    year_cond = (year % 4 == 0) & (year % 100 != 0)

    # Check if the input year meets either condition.
    result = century_cond or year_cond

    return result


def start_year(filename,
               ):
    """
    For a single file, get the start year of the winter season in which all
    cyclone track data within the file are indexed to, based on its filename.

    Arguments:
    ---------------------------------------------------------------------------
    filename (str) -- Name of file containing all tracks for a single season.

    Returns:
    ---------------------------------------------------------------------------
    The start year of the winter season during which all cyclones described in
    the given text file occur.
    """
    # Get the single substring in filename containing 8 consecutive digits.
    substring = re.findall("(\d{8})", filename)[0]

    # Extract start year (first 4 digits) and convert to integer.
    year = int(substring[0:4])

    return year


def time_series(start_year,
                period,
                ):
    """
    Get the first and final measurement times in the winter season (start of
    December to end of February) beginning in a given year.

    Arguments:
    ---------------------------------------------------------------------------
    start_year (int) -- The start year of the winter season.
    period (float)   -- The interval between measurements [units: hours].

    Returns:
    ---------------------------------------------------------------------------
    A series containing all dates and times within the given season.
    """
    # Start of each season is 1st December at midnight.
    start_time = np.datetime64(f"{start_year}-12-01T00")

    # Number of days in Feb depends on whether next year is leap or not.
    days_in_feb = 29 if is_leap_year(start_year + 1) else 28

    # Calculate number of periods across the season.
    day_count = 62 + days_in_feb # Always 62 days in Dec and Jan combined.
    period_count = day_count * 24 / period

    # Produce time series for season with delta period intervals.
    time_series = pd.date_range(start_time,
                                periods=period_count,
                                freq=f"{period}H",
                                )

    return time_series


def shifted_times(median_time,
                  shift_period,
                  ):
    """
    For a given median time, calculate the new times after shifting before and
    ahead by a certain period (equivalent in both time directions).

    Arguments:
    ---------------------------------------------------------------------------
    median_time (np.datetime64) -- The central time between the bounds.
    shift_period (int)          -- The time before and ahead of the cyclonic
                                   centre with impacted winds [units: hours].

    Returns:
    ---------------------------------------------------------------------------
    A tuple containing the new times (as np.datetime64).
    """
    # Create timedelta based on period.
    shift = np.timedelta64(shift_period, "h")

    # Calculate time bounds before and ahead of central time.
    earliest_time = median_time - shift
    latest_time = median_time + shift

    return earliest_time, latest_time
