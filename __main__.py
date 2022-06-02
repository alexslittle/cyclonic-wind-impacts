#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri 14 Jan 2022

@author: Alex Little

Core script to calculate maximum wind speed footprints across Europe for all
cyclone tracks.

For each combination of epoch and specific model covered in the study, reads
the wind field and cyclone track data from the /climate-data directory. Then
computes the maximum wind speeds attributable to each cyclone, for each grid-
point within the Europe domain. Each individual footprint is saved to the
/climate-data directory after it has been generated.
"""
# Built-in libs.
import os
from glob import iglob

# Standard libs.
import xarray as xr
from tqdm import tqdm

# Package modules.
from funcs import *


def main():
    # --- Data input. ---

    # Path to individual climate data experiments.
    DATA_PATH = "cyclonic-wind-footprints/data/historical/ERA5"

    # Geographical bounds of study spatial [units: DD]. The bounds
    # of each axis must be seperated by a multiple of the resolution.
    WEST_BOUND = -23.4375
    EAST_BOUND = 30.9375
    SOUTH_BOUND = 35.0625
    NORTH_BOUND = 70.6875

    # First data index for each track (0-indexed or 1-indexed).
    FIRST_TRACK_INDEX = 1
    # Grid resolution [units: DD].
    RESOLUTION = 1.875
    # Interval between wind/track measurements [units: hours].
    PERIOD = 6
    # Time before/ahead of cyclonic centre with impacted winds [units: hours].
    IMPACT_DURATION = 12
    # Radius around cyclonic centre with impacted winds [units: DD].
    IMPACT_RADIUS = 5.

    # --- Analysis. ---

    # Pack bounds.
    lon_bounds = (WEST_BOUND, EAST_BOUND)
    lat_bounds = (SOUTH_BOUND, NORTH_BOUND)

    # Get array of all longitude grid-points.
    lon_vector = domain.build_vector(*lon_bounds,
                                     RESOLUTION,
                                     )

    # Get array of all latitude grid-points.
    lat_vector = domain.build_vector(*lat_bounds,
                                     RESOLUTION,
                                     )

    # Build 2D grid covering domain.
    grid = domain.build_grid(*lon_bounds,
                             *lat_bounds,
                             RESOLUTION,
                             )

    # Get list of all epoch/model combinations.
    experiments = list(iglob(DATA_PATH))

    # Iterate over each experiment.
    for root in tqdm(experiments,
                     total=len(experiments),
                     position=0,
                     leave=False,
                     desc="EXPT",
                     colour="red",
                     ):

        # Get the epoch and model of the current experiment.
        prefix = "_".join(root.split(os.sep)[2:])

        # Load simulated wind data.
        wind_path = os.path.join(root,
                                 prefix + "_sfcWind.nc",
                                 )
        wind_field = xr.open_dataset(wind_path)

        # List individual track files (ignore hidden files).
        tracks_path = os.path.join(root,
                                   "track-coords",
                                   )
        track_files = [f for f in os.listdir(tracks_path)
                       if not f.startswith(".")]

        # Iterate over each track file.
        for file in tqdm(sorted(track_files),
                         total=len(track_files),
                         position=1,
                         leave=False,
                         desc="SEAS",
                         colour="yellow",
                         ):

            # Get start year of winter season.
            start_year = season.start_year(file)

            # Get time range covering this winter season.
            time_series = season.time_series(start_year,
                                             PERIOD,
                                             )

            # Load and separate all tracks in file.
            single_path = os.path.join(tracks_path,
                                       file,
                                       )
            all_tracks = tracks.read(single_path)

            # Iterate over individual cyclone tracks in file.
            for index, track in tqdm(enumerate(all_tracks),
                                     total=len(all_tracks),
                                     position=2,
                                     leave=False,
                                     desc="TRCK",
                                     colour="green",
                                     ):

                # Converts a value in a domain of [0, 360] to [-180, 180].
                # convert_domain = lambda x: (x + 180) % 360 - 180
                def convert_domain(x): return (x + 180) % 360 - 180

                # Adjust longitudinal domain.
                track.lon = track.lon.transform(convert_domain)

                # Convert seasonal time indices to datetimes.
                track.time = time_series[track.time - FIRST_TRACK_INDEX]

                # Iterate over individual track points of cyclone.
                point_footprints = list()
                for __, point in track.iterrows():

                    # Check if each point along the track is in the domain.
                    point_in_domain = domain.contains_point(point.lon,
                                                            point.lat,
                                                            *lon_bounds,
                                                            *lat_bounds,
                                                            )

                    # Compute footprint if track point is inside the domain.
                    if point_in_domain:

                        # Get earliest and latest times to slice wind data.
                        time_limits = season.shifted_times(point.time,
                                                           IMPACT_DURATION,
                                                           )

                        # Get maximum wind speeds around the current point.
                        footprint = point_footprint(point.lon,
                                                    point.lat,
                                                    point.time,
                                                    lon_vector,
                                                    lat_vector,
                                                    grid,
                                                    time_limits,
                                                    wind_field,
                                                    IMPACT_RADIUS,
                                                    RESOLUTION,
                                                    )
                        point_footprints.append(footprint)

                    # Don't compute footprint if track point isn't in domain.
                    else:
                        pass

                try:
                    # Merge footprints at each cyclone point into single array.
                    merged_footprints = xr.concat(point_footprints,
                                                  dim="time",
                                                  )

                    # Create unique identifier name for track.
                    filename = tracks.output_filename(file,
                                                      index + 1,
                                                      )

                    # Export footprint.
                    output_filepath = os.path.join(root,
                                                   "output-footprints",
                                                   filename,
                                                   )
                    merged_footprints.to_netcdf(output_filepath)

                except:
                    pass


if __name__ == "__main__":
    main()
