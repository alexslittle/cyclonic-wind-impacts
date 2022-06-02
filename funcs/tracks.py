#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Standard libs.
import pandas as pd

# Suppress SettingWithCopy warnings.
pd.options.mode.chained_assignment = None


def read(filepath,
         ):
    """
    Load all cyclone track data contained in a single text file, split data for
    individual tracks into seperate dataframes, and append each dataframe to a
    list.

    Arguments:
    ---------------------------------------------------------------------------
    filepath (str or path object) -- Path to a text file containing track data
                                     for multiple individual cyclones.

    Returns:
    ---------------------------------------------------------------------------
    A list of dataframes, each of which describes the geographical coordinates
    (lon, lat) of a single track at a given time. Based on the current method
    in which track files are produced, this list contains track data for all
    cyclones in the single winter season defined by the filename.
    """
    # Read all track data for a single winter season.
    all_tracks = pd.read_csv(filepath,
                             sep="\s+", # Data is space-delimited.
                             names=["time", # Only import time/lon/lat info.
                                    "lon",
                                    "lat"],
                             usecols=list(range(3)),
                             skiprows=3, # No data in first three rows.
                             )

    # Get row indices where info for the next track starts.
    rows_to_split = split_indices(all_tracks)

    # Append data for tracks to an empty list.
    seperated_tracks = list()
    for index, __ in enumerate(rows_to_split[:-1]):
        find_track = single_track_indices(index,
                                          rows_to_split)
        track = all_tracks.iloc[slice(*find_track)]
        track.time = track.time.astype(int)
        seperated_tracks.append(track)

    return seperated_tracks


def split_indices(df,
                  ):
    """
    Locate the row indices within an input dataframe at which data for one
    cyclone track ends, and data for the next track begins.

    Arguments:
    ---------------------------------------------------------------------------
    df (DataFrame or named Series) -- The dataframe describing cyclone tracks.

    Returns:
    ---------------------------------------------------------------------------
    A list of row indices where a single condition used to establish whether
    a given row is the start of a new cyclone track evaluates as True.
    """
    # "TRACK_ID" appears in the time column at the start of each new track.
    condition = df["time"] == "TRACK_ID"
    # Indices where condition is true.
    indices = df.index[condition]
    final_index = len(df) - 1
    indices = list(indices) + [final_index]

    return indices


def single_track_indices(track_index,
                         split_at_rows,
                         ):
    """
    Get the index values at which to slice rows from the imported raw data, in
    order to extract data for a single track.

    Arguments:
    ---------------------------------------------------------------------------
    track_index (int)    -- The current track within the raw data (indexed).
                            Tracks within the raw data are indexed from 0 to n,
                            where n is the number of unique tracks.
    split_at_rows (list) -- A list of integers corresponding to the row indices
                            within the raw data at which a new track starts.

    Returns:
    ---------------------------------------------------------------------------
    A tuple containing the row index values between which data for a single
    track is located within the raw text file.
    """
    # Omit the first two rows for each individual track, which contain
    # unneeded metadata.
    start_index = split_at_rows[track_index] + 2
    end_index = split_at_rows[track_index + 1]

    return start_index, end_index


def output_filename(file,
                    track_index,
                    ):
    """
    Create unique output filename for given track.

    Arguments:
    ----------
    file (str)
        * The filename of input track data for a given season.
    track_index (int)
        * The index of a track within a given season.

    Returns:
    ----------
    str.
    """
    # Remove substring from input filename.
    name = file.split("TRACKS", 1)[0]

    # Add zeroes before index until string has length 3.
    index_string = str(track_index)
    zfill_string = index_string.zfill(3)

    # Create new filename that identifies by track index.
    string = name + "TRACK_" + zfill_string + ".nc"

    return string
