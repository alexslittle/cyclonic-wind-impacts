#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Standard libs.
import pandas as pd
import xarray as xr

# Package modules.
from . import domain, season


def point_footprint(lon_point,
                    lat_point,
                    time_point,
                    lon_vector,
                    lat_vector,
                    grid,
                    time_bounds,
                    wind_field,
                    impact_radius,
                    resolution,
                    ):
    """
    Gets the maximum near-surface wind speeds at each grid-point of the domain
    across a certain range of time, for a single track point. The values are
    masked over all grid-points located outside of a given radius surrounding
    the track point.

    Arguments:
    ----------

    Returns:
    ----------
    xarray.DataArray (2-D).
    """
    # Get nearest grid index of point longitude.
    lon_index = domain.nearest_index(lon_vector,
                                     lon_point,
                                     )

    # Get nearest grid index of point latitude.
    lat_index = domain.nearest_index(lat_vector,
                                     lat_point,
                                     )

    # Create mask array around centre point.
    cyclone_driven = domain.circle_mask(lon_index,
                                      lat_index,
                                      *grid,
                                      impact_radius,
                                      resolution,
                                      )

    # Apply track's spatial and time constraints to wind field.
    field = wind_field.sel(time=slice(*time_bounds)).max("time")
    masked_field = field.where(cyclone_driven)
    time_index = pd.DatetimeIndex([time_point])
    time_da = xr.DataArray(data=time_index,
                           coords=[("time", time_index)])
    time_label = masked_field.expand_dims({"time": time_da})

    return masked_field
