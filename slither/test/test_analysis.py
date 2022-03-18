import numpy as np
from slither.core.analysis import (
    check_coords, interpolate_nan, filtered_heartrates, appropriate_partition,
    elevation_summary)
from numpy.testing import assert_almost_equal
from nose.tools import assert_equal


def test_check_coords():
    coords = np.array([[0, 1], [np.nan, 2], [2, 3]])
    checked_coords = check_coords(coords)
    assert_almost_equal(checked_coords, np.array([[0, 1], [2, 3]]))


def test_interpolate_nan():
    a = np.array([0, 1, np.nan, 3, 4, 5])
    b = interpolate_nan(a)
    assert_almost_equal(b, [0, 1, 2, 3, 4, 5])


def test_filtered_heartrates():
    path = {"heartrates": np.array([100, 101, 100, 101, 104])}
    hrs = filtered_heartrates(path, 3)
    assert_almost_equal(hrs, [100, 100, 101, 101, 101])


def test_appropriate_partition():
    assert_equal(appropriate_partition(1000), 400)
    assert_equal(appropriate_partition(10000), 1000)
    assert_equal(appropriate_partition(30000), 2000)
    assert_equal(appropriate_partition(50000), 5000)
    assert_equal(appropriate_partition(200000), 10000)


def test_elevation_summary():
    gain, loss, slope_in_percent = elevation_summary(
        altitudes=[0.0, 1.0], total_distance_in_m=1.0)
    assert_equal(gain, 1.0)
    assert_equal(loss, 0.0)
    assert_equal(slope_in_percent, 100.0)

    gain, loss, slope_in_percent = elevation_summary(
        altitudes=[1.0, 0.0], total_distance_in_m=1.0)
    assert_equal(gain, 0.0)
    assert_equal(loss, 1.0)
    assert_equal(slope_in_percent, 0.0)