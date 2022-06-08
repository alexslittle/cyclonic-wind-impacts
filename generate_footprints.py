#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@File    :   generate_footprints.py
@Date    :   2022-06-03
@Author  :   Alex Little
@Desc    :   Calculate wind speed footprints for individual cyclone tracks
"""

# --------------------------------------------------------------------------------

# Built-in modules
from pathlib import Path

# PyPI packages
import numpy as np
import pandas as pd
import xarray as xr
from tqdm import tqdm

# Side modules
from base_funcs import _start_year, _season_range, _track_indices, _circle_mask, _shift_time
from params import *

# Construct 1-D vectors containing lat and lon grid-points
lat_vector = np.arange(south_bound, north_bound + resolution, resolution)
lon_vector = np.arange(west_bound, east_bound + resolution, resolution)

# Construct 2-D grid covering domain
lat_grid, lon_grid = np.mgrid[south_bound: north_bound + resolution: resolution,
                              west_bound: east_bound + resolution: resolution]

# Loop through experiments
for experiment in tqdm(sorted(experiments),
                       total=len(experiments),
                       position=1,
                       leave=False,
                       desc="EXPERIMENT",
                       colour="magenta",
                       ):

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

            # No observations on leap days given for the BCC-CSM2-MR model
            leap_days = False if model == "BCC-CSM2-MR" else True

            # Read wind field data for the given experiment and model
            wind_field = xr.open_dataset(
                filename_or_obj=Path(
                    f"./data/sfcWind/{experiment}/sfcWind_{experiment}_{model}.nc",
                )
            )

            # List individual track files (ignore hidden files)
            track_files = [f for f in Path(f"./data/tracks/{experiment}/{model}").iterdir()
                           if not f.name.startswith(".")]

            # Create subdirectory to contain output footprints
            subdir = Path(f"./outputs/footprints/{experiment}/{model}/")
            subdir.mkdir(parents=True, exist_ok=True)

            for path in tqdm(sorted(track_files),
                             total=len(track_files),
                             position=3,
                             leave=False,
                             desc="SEASON",
                             colour="yellow",
                             ):

                # Get the start year of the winter covered by the track file
                season_start = _start_year(path.name)

                # Generate winter time series
                time_series = _season_range(season_start, leap_days)

                # Load and separate all individual tracks in the file
                all_tracks = pd.read_csv(filepath_or_buffer=path,
                                         sep=r"\s+",  # Space delimited
                                         names=["time",
                                                "lon",
                                                "lat"],
                                         usecols=list(range(3)),
                                         skiprows=3,  # No data in the first three rows of each text file
                                         )

                # Get row indices where "TRACK_ID" appears in the time column at the start of each new track
                indices = all_tracks.index[all_tracks["time"] == "TRACK_ID"]
                rows_to_split = list(indices) + [len(all_tracks) - 1]  # Append final index to the end of the list

                # Split data for each track into separate dataframes
                seperated_tracks = []
                for index in range(len(rows_to_split) - 1):

                    track = all_tracks.iloc[slice(*_track_indices(index, rows_to_split))]
                    track.time = track.time.astype(int)
                    seperated_tracks.append(track)

                # Initialise track index
                track_index = 1

                # Iterate over each individual track
                for track in tqdm(seperated_tracks,
                                  total=len(seperated_tracks),
                                  position=4,
                                  leave=False,
                                  desc="TRACK",
                                  colour="green",
                                  ):

                    # Adjust longitudinal domain
                    track.lon = track.lon.transform(lambda x: (x + 180) % 360 - 180)

                    # Convert seasonal time indices to datetimes
                    track.time = time_series[track.time - 1]

                    # Iterate over individual track points of cyclone
                    point_footprints = []
                    for __, point in track.iterrows():

                        # Compute footprint if track point is inside the domain
                        if west_bound <= point.lon <= east_bound and south_bound <= point.lat <= north_bound:

                            # Get point time data
                            time_index = pd.DatetimeIndex([point.time])
                            time_da = xr.DataArray(data=time_index,
                                                   coords=[("time", time_index)])

                            # Get the nearest grid index of point lon and lat from the corresponding vector
                            lat_index, lon_index = map(lambda l, v: min(l, key=lambda n: abs(v - n)),
                                                       [lat_vector, lon_vector], [point.lat, point.lon])

                            # Create mask array around centre point
                            impact_zone = _circle_mask(lat_index,
                                                       lon_index,
                                                       lat_grid,
                                                       lon_grid,
                                                       impact_radius,
                                                       resolution,
                                                       )

                            # Get maximum wind speeds around the current point
                            point_footprint = wind_field.sel(
                                time=slice(*_shift_time(point.time, impact_duration))
                            ).max(
                                "time"  # Maximum wind speed within impact duration
                            ).where(
                                impact_zone  # Mask outside cyclone impact radius
                            ).expand_dims(
                                {"time": time_da}  # Re-add time info
                            )
                            point_footprints.append(point_footprint)

                        # Don't compute footprint if track point isn't in domain
                        else:
                            pass

                    try:
                        # Merge footprints at each cyclone point into a single dataset
                        wind_footprint = xr.concat(point_footprints,
                                                   dim="time",
                                                   )

                        # Create a unique identifier name for the file
                        track_id = f"{season_start}{season_start + 1}_{str(track_index).zfill(3)}"
                        track_index = track_index + 1

                        wind_footprint.to_netcdf(
                            path=f"{subdir}/footprints_{experiment}_{model}_{track_id}.nc",
                        )

                    # Pass if no track point entered domain
                    except ValueError:
                        pass
