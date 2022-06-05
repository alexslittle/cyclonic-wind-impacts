#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
@File    :   footprints.py
@Date    :   2022/06/03
@Author  :   Alex Little
@Desc    :   Calculate wind speed footprints for individual cyclone tracks
"""

# --------------------------------------------------------------------------------

# Built-in modules
from pathlib import Path

# conda-installed modules
import numpy as np
import pandas as pd
import xarray as xr
from tqdm import tqdm

# Side modules
from lib import *
from params import *


def main(experiment: str,
         model: str,
         lat_vector: np.ndarray,
         lon_vector: np.ndarray,
         lat_grid: np.ndarray,
         lon_grid: np.ndarray,
         wind_field: xr.Dataset,
         ):

    # No observations on leap days given for the BCC-CSM2-MR model
    if model == "BCC-CSM2-MR":
        leap_days = False
    else:
        leap_days = True

    # List individual track files (ignore hidden files)
    track_files = [f for f in Path(f"./cyclonic-wind-impacts/data/tracks/{experiment}/{model}").iterdir()
                   if not f.name.startswith(".")]

    for path in tqdm(sorted(track_files),
                     total=len(track_files),
                     position=3,
                     leave=False,
                     desc="SEASON    ",
                     colour="yellow",
                     ):

        # Get time series of the winter covered by the track file
        time_series = season_range(start_year(path.name),
                                   leap_days)

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

            track = all_tracks.iloc[slice(*track_indices(index, rows_to_split))]
            track.time = track.time.astype(int)
            seperated_tracks.append(track)

        # Initialise track index
        track_index = 1

        # Iterate over each individual track
        for track in tqdm(seperated_tracks,
                          total=len(seperated_tracks),
                          position=4,
                          leave=False,
                          desc="TRACK     ",
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

                    # Get the nearest grid index of point lon and lat
                    lat_index = min(lat_vector, key=lambda n: abs(point.lat - n))
                    lon_index = min(lon_vector, key=lambda n: abs(point.lon - n))

                    # Create mask array around centre point
                    impact_zone = circle_mask(lat_index,
                                              lon_index,
                                              lat_grid,
                                              lon_grid,
                                              impact_radius,
                                              resolution,
                                              )

                    # Get maximum wind speeds around the current point
                    point_footprint = wind_field.sel(
                        time=slice(*shift_time(point.time, impact_duration))
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
                # Create subdirectory to contain output footprints
                subdir = Path(f"./cyclonic-wind-impacts/outputs/footprints/{experiment}/{model}/")
                subdir.mkdir(parents=True, exist_ok=True)

                # Create a unique identifier name for the file
                id_string = str(track_index).zfill(3)
                track_index = track_index + 1

                wind_footprint.to_netcdf(
                    path=f"{subdir}/footprints_{experiment}_{model}_{id_string}.nc",
                )

            # Pass if no track point entered domain
            except ValueError:
                pass
