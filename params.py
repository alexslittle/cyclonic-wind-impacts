#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# 2-D rectilinear domain bounds (units: decimal degs)
west_bound = -23.4375
east_bound = 30.9375
south_bound = 35.0625
north_bound = 70.6875
grid_resolution = 1.875

# Radius around cyclonic centre with impacted winds (units: decimal degs)
impact_radius = 5

# Time before/ahead of cyclonic centre with impacted winds (units: h)
impact_duration = 12

# Minimum possible wind speed that can cause damage (units: m/s)
impact_threshold = 9

# List experiment combinations
experiments = [
    "historical",
    "ssp245",
    "ssp585"
]

# List model combinations (include ERA5 reanalysis model)
models = [
    "ACCESS-CM2",
    "BCC-CSM2-MR",
    "EC-Earth3",
    "ERA5",
    "KIOST-ESM",
    "MIROC6",
    "MPI-ESM1-2-HR",
    "MPI-ESM1-2-LR",
    "MRI-ESM2-0"
]
