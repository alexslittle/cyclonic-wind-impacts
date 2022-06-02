#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# Standard libs.
import numpy as np


def build_vector(min_bound,
                 max_bound,
                 step,
                 ):
    """
    Get array of values between two bounds, separated by fixed steps.

    Arguments:
    ----------
    min_bound, max_bound (float)
        * The desired limits of the vector.
    step (float)
        * The spacing between values.

    Returns:
    ----------
    numpy.ndarray (1-D).
    """
    # Define start and stop bounds.
    start = min_bound

    # The np.arange function does not include the stop value, so must extend.
    stop = max_bound + step

    # Create vector with fixed spacing.
    vector = np.arange(start,
                       stop,
                       step)

    return vector


def build_grid(west_bound,
               east_bound,
               south_bound,
               north_bound,
               resolution,
               ):
    """
    Create a rectilinear grid bounded by given geographic coordinates.

    Arguments:
    ----------
    west_bound, east_bound, south_bound, north_bound (float)
        * The bounds of the domain [units: DD].
    resolution (float)
        * The interval between grid-points [units: DD].

    Returns:
    ----------
    numpy.ndarray (2-D).
    """
    # Define start and stop bounds.
    x_start = west_bound
    y_start = south_bound

    # The np.mgrid function does not include the stop value, so must extend.
    x_stop = east_bound + resolution
    y_stop = north_bound + resolution

    # Build grid.
    x_grid, y_grid = np.mgrid[x_start: x_stop: resolution,
                              y_start: y_stop: resolution,
                              ]

    return x_grid, y_grid


def contains_point(lon,
                   lat,
                   west_bound,
                   east_bound,
                   south_bound,
                   north_bound,
                   ):
    """
    Test if a point falls within a rectilinear geographical domain.

    Arguments:
    ----------
    lon, lat (float)
        * Coordinates of the test point [units: DD].
    west_bound, east_bound, south_bound, north_bound (float)
        * The bounds of the domain [units: DD].

    Returns:
    ----------
    Bool.
    """
    # Test if each coordinate is within the corresponding bounds.
    contains_lon = west_bound <= lon <= east_bound
    contains_lat = south_bound <= lat <= north_bound

    # Both of above conditions must be met.
    result = contains_lon and contains_lat

    return result


def nearest_index(values,
                  target_value,
                  ):
    """
    Finds the index of a list element whose value is closest to a target value.

    Arguments:
    ----------
    values (list)
        * List containing all possible values.
    target_value (float)
        * The value whose closest match is to be found.

    Returns:
    ----------
    int.
    """
    # Generate sequence of possible index values.
    value_indices = range(len(values))

    # Gets the absolute difference between the target and a given list element.
    # key_func = lambda n: abs(target_value - values[n])
    key_func = lambda n: abs(target_value - n)

    # Find the index for which the key function evaluates to a minimum.
    # index = min(value_indices,
    #             key=key_func,
    #             )
    index = min(values,
                key=key_func,
                )

    return index


def circle_mask(lon_centre,
                lat_centre,
                lon_grid,
                lat_grid,
                radius,
                resolution,
                ):
    """
    Create a circular mask centred at given geographical coordinates.

    Arguments:
    ----------
    lon_centre, lat_centre (float)
        * Coordinates of the centre point [units: DD].
    lon_grid, lat_grid (numpy.ndarray)
        * Grid coordinate matrices.
    radius (float)
        * Radius of circular mask [units: DD].
    resolution (float)
        * Grid resolution [units: DD].

    Returns:
    ----------
    numpy.ndarray (2-D, bool).
    """
    # Calculate radius of circle on the grid.
    grid_radius = radius / resolution

    # Calculate distance of each point from the circle centre.
    lon_dist = lon_grid - lon_centre
    lat_dist = lat_grid - lat_centre
    dist_from_centre = np.sqrt(lon_dist**2 + lat_dist**2)

    # Mask all points outside the circle.
    mask = dist_from_centre <= grid_radius

    return mask
