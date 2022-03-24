import numpy as np
from slither.core.geodetic import (
    haversine_dist, dist_on_earth, compute_velocities)
from nose.tools import assert_less, assert_almost_equal
from numpy.testing import assert_array_almost_equal


def test_compare_haversine_pyproj():
    lat_roland, long_roland = np.deg2rad([53.0759, 8.80731])
    lat_sol, long_sol = np.deg2rad([40.689249, -74.0445])
    hdistance = haversine_dist(lat_roland, long_roland, lat_sol, long_sol)
    distance = dist_on_earth(lat_roland, long_roland, lat_sol, long_sol)
    difference = abs(hdistance - distance)
    relative_difference = difference / distance
    assert_less(relative_difference, 0.003)


def test_compute_velocities_equal_timestamps():
    timestamps = np.array([0, 1, 1])
    coords = np.deg2rad([
        [53.0759, 8.80731], [53.076, 8.80731], [53.0761, 8.80731]])
    velocities, total_distance = compute_velocities(timestamps, coords)
    assert_array_almost_equal(velocities, [0.0, 11.12876992, 11.12876992])
    assert_almost_equal(total_distance, 11.128769923727916)
