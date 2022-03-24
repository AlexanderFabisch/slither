import numpy as np
from slither.core.analysis import (
    check_coords, interpolate_nan, filtered_heartrates, appropriate_partition,
    elevation_summary, get_paces, is_outlier)
from slither.loader import FitLoader
from numpy.testing import assert_array_equal
from nose.tools import assert_equal, assert_almost_equal


def test_check_coords():
    coords = np.array([[0, 1], [np.nan, 2], [2, 3]])
    checked_coords = check_coords(coords)
    assert_array_equal(checked_coords, np.array([[0, 1], [2, 3]]))


def test_interpolate_nan():
    a = np.array([0, 1, np.nan, 3, 4, 5])
    b = interpolate_nan(a)
    assert_array_equal(b, [0, 1, 2, 3, 4, 5])


def test_filtered_heartrates():
    path = {"heartrates": np.array([100, 101, 100, 101, 104])}
    hrs = filtered_heartrates(path, 3)
    assert_array_equal(hrs, [100, 100, 101, 101, 101])


def test_appropriate_partition():
    assert_equal(appropriate_partition(1000), 400)
    assert_equal(appropriate_partition(10000), 1000)
    assert_equal(appropriate_partition(30000), 2000)
    assert_equal(appropriate_partition(50000), 5000)
    assert_equal(appropriate_partition(200000), 10000)


def test_is_outlier_1d():
    points = [0, 1, 2, 30, 4, 5, 6]
    mask = is_outlier(points)
    assert_array_equal(mask, [False, False, False, True, False, False, False])


def test_is_outlier_2d():
    points = [[0, 0], [1, 1], [2, 2], [3, 30], [4, 4], [5, 5], [6, 6]]
    mask = is_outlier(points)
    assert_array_equal(mask, [False, False, False, True, False, False, False])


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


def test_get_paces():
    fit_loader = FitLoader(filename="test_data/running.fit")
    activity = fit_loader.load()
    path = activity.get_path()
    paces = get_paces(path, activity.sport)
    assert_equal(paces[0][0], 1000)
    assert_equal(paces[1][0], 2000)
    assert_equal(paces[2][0], 3000)
    assert_equal(paces[3][0], 4000)
    assert_equal(paces[4][0], 5000)
    assert_equal(paces[5][0], 6000)
    assert_equal(paces[6][0], 7000)
    assert_equal(paces[0][1], 369)
    assert_equal(paces[1][1], 353)
    assert_equal(paces[2][1], 363)
    assert_equal(paces[3][1], 388)
    assert_equal(paces[4][1], 361)
    assert_equal(paces[5][1], 384)
    assert_equal(paces[6][1], 391)


def test_get_paces_empty_path():
    path = {"timestamps": np.array([]), "velocities": np.array([])}
    paces = get_paces(path, "running")
    assert_equal(len(paces), 0)
