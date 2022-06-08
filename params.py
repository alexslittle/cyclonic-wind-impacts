#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# --------------------------------------------------------------------------------

# 2-D rectilinear domain bounds (units: degs) – float
west_bound = -23.4375
east_bound = 30.9375
south_bound = 35.0625
north_bound = 70.6875
resolution = 1.875

# Radius around cyclonic centre with impacted winds (units: degs) – float
impact_radius = 5

# Time before/ahead of cyclonic centre with impacted winds (units: h) – int
impact_duration = 12

# Minimum possible wind speed that can cause damage (units: m s-1) – float
impact_threshold = 9

# List experiment/model combinations – include ERA5 reanalysis model
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
