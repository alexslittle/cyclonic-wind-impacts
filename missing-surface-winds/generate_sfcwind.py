#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@File    :   generate_sfcwind.py
@Date    :   2022/06/02
@Author  :   Alex Little
@Desc    :   Generate surface wind datasets from input wind velocity component variables
"""

# --------------------------------------------------------------------------------

# Built-in modules
import calendar
from datetime import datetime

# pip-installed modules
import dask
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr
import xesmf as xe

dask.config.set(**{"array.slicing.split_large_chunks": False})

LON_MIN, LON_MAX = -23.4375, 30.9375
LAT_MIN, LAT_MAX = 35.0625, 70.6875
GRID_RESOLUTION = 1.875

YEAR_START = 2070
YEAR_END = 2100

if calendar.isleap(YEAR_END):
    days_in_february = 29
else:
    days_in_february = 28

source_id = "BCC-CSM2-MR"
experiment_id = "ssp585"
variant_label = "r1i1p1f1"


def read_files(variable):
    ds = xr.open_mfdataset(
        paths=f"./missing-surface-winds/{variable}/*.nc",
        chunks={"time": 100},
        engine="netcdf4",
        parallel=True,
    ).rename(
        {"lon": "longitude", "lat": "latitude"}
    ).drop_vars(
        "height"
    )

    ds = ds.assign_coords(
        time=ds.indexes["time"].to_datetimeindex(),
        longitude=(((ds.longitude + 180) % 360) - 180)
    ).sortby(
        ["time", "longitude"]
    ).sel(
        time=ds.time.dt.month.isin([1, 2, 12])
    ).sel(
        time=slice(
            f"{YEAR_START}-12-01 00:00",
            f"{YEAR_END}-02-{days_in_february} 18:00",
            2
        ),
        longitude=slice(
            LON_MIN - 2 * GRID_RESOLUTION, LON_MAX + 2 * GRID_RESOLUTION
        ),
        latitude=slice(
            LAT_MIN - 2 * GRID_RESOLUTION, LAT_MAX + 2 * GRID_RESOLUTION
        ),
    )

    return ds[variable]


def regrid_data(ds):

    ds_out = xr.Dataset(
        {"time": (["time"], ds.time.values),
         "latitude": (["latitude"], np.arange(LAT_MIN, LAT_MAX + GRID_RESOLUTION, GRID_RESOLUTION)),
         "longitude": (["longitude"], np.arange(LON_MIN, LON_MAX + GRID_RESOLUTION, GRID_RESOLUTION))}
    )

    regridder = xe.Regridder(
        ds, ds_out, "conservative"
    )

    a = regridder(ds, keep_attrs=True)
    return a


def main():
    ds = xr.merge(
        [read_files("uas"), read_files("vas")],
        combine_attrs="drop",
    )

    ds["sfcWind"] = xr.apply_ufunc(lambda u, v: np.sqrt(u ** 2 + v ** 2),
                                   ds.uas,
                                   ds.vas,
                                   dask="allowed",
                                   )

    ds = ds.drop_vars(
        ["uas", "vas"]
    ).assign_attrs(
        {"standard_name": "wind_speed",
         "long_name": "Near-Surface Wind Speed",
         "short_name": "ws",
         "units": "m s-1",
         "source_id": source_id,
         "experiment_id": experiment_id,
         "variant_label": variant_label,
         "description": "The magnitude of horizontal air movement at the near-surface (10 m)",
         "history": f"{datetime.now()} created by {__file__}"}
    )

    ds = regrid_data(ds)
    ds.isel(time=0)["sfcWind"].plot()
    plt.show()

    ds.to_netcdf(
        path=f"./missing-surface-winds/sfcWind_{experiment_id}_{source_id}.nc",
        compute=True
    )


if __name__ == "__main__":
    main()

