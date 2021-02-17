import numpy as np
from slither.ui_text import (convert_mps_to_kmph, time_representation,
                             DataDisplay)
from slither.preprocessing import is_outlier, dist_on_earth, check_coords
from numpy.testing import assert_array_equal
from nose.tools import assert_almost_equal, assert_equal


def test_convert_mps_to_kmph():
    assert_equal(convert_mps_to_kmph(1.0), 3.6)


def test_time_representation():
    assert_equal(time_representation(2, 10, 35), 7835.0)


def test_haversine_dist():
    d = dist_on_earth(0.0, 0.0, 0.0, 0.0)
    assert_almost_equal(d, 0.0)
    d = dist_on_earth(np.zeros(3), np.zeros(3), np.zeros(3), np.zeros(3))
    assert_equal(d.shape, (3,))


def test_check_coords():
    coords = np.array([
        [np.inf, 0.0],
        [1.0, np.nan],
        [np.nan, np.inf],
        [2.0, 3.0]
    ])
    valid_coords = check_coords(coords)
    assert_array_equal(valid_coords, np.array([[2.0, 3.0]]))


def test_distance():
    data_display = DataDisplay()
    assert_equal(data_display.display_distance(0.0), "-")
    assert_equal(data_display.display_distance(5000.0), "5 km")
    assert_equal(data_display.display_distance(400.6), "401 m")
    assert_equal(data_display.display_distance(12326.0), "12.33 km")


def test_display_time():
    data_display = DataDisplay()
    assert_equal(data_display.display_time(0.0), "-")
    assert_equal(data_display.display_time(np.inf), "NA")
    assert_equal(data_display.display_time(61), "00:01:01 h")
    assert_equal(data_display.display_time(3601), "01:00:01 h")


def test_display_calories():
    data_display = DataDisplay()
    assert_equal(data_display.display_calories(0.0), "-")
    assert_equal(data_display.display_calories(1532.0), "1532 kCal")


def test_display_heartrate():
    data_display = DataDisplay()
    assert_equal(data_display.display_heartrate(0.0), "-")
    assert_equal(data_display.display_heartrate(234.0), "234 bpm")


def test_is_outlier():
    outliers = is_outlier(np.array([1, 2, 3]))
    assert_array_equal(outliers, np.array([False, False, False]))
    outliers = is_outlier(np.array([1, 2, 3, 10]))
    assert_array_equal(outliers, np.array([False, False, False, True]))
    outliers = is_outlier(np.array([-10, 1, 2, 3, 10]))
    assert_array_equal(outliers, np.array([True, False, False, False, True]))
    outliers = is_outlier(np.array([-9, 1, 11]))
    assert_array_equal(outliers, np.array([False, False, False]))
