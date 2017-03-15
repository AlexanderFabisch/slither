import numpy as np
from slither.data_utils import haversine_dist, is_outlier
from numpy.testing import assert_array_equal
from nose.tools import assert_almost_equal, assert_equal


def test_haversine_dist():
    d = haversine_dist(0.0, 0.0, 0.0, 0.0)
    assert_almost_equal(d, 0.0)
    d = haversine_dist(0.5 * np.pi, 0.0, 0.0, 0.0, 23.45)
    assert_almost_equal(d, 0.5 * np.pi * 23.45)
    d = haversine_dist(0.0, np.pi, 0.0, 0.0, 34.56)
    assert_almost_equal(d, np.pi * 34.56)
    d = haversine_dist(np.zeros(3), np.zeros(3), np.zeros(3), np.zeros(3))
    assert_equal(d.shape, (3,))


def test_is_outlier():
    outliers = is_outlier(np.array([0, 1, 2]))
    assert_array_equal(outliers, np.array([False, False, False]))
    outliers = is_outlier(np.array([0, 1, 2, 10]))
    assert_array_equal(outliers, np.array([False, False, False, True]))
    outliers = is_outlier(np.array([-10, 0, 1, 2, 10]))
    assert_array_equal(outliers, np.array([True, False, False, False, True]))
    outliers = is_outlier(np.array([-10, 0, 10]))
    assert_array_equal(outliers, np.array([False, False, False]))
