import numpy as np
from slither.core import unit_conversions
from nose.tools import assert_equal
from numpy.testing import assert_array_almost_equal


def test_semicircles_to_radians():
    assert_equal(unit_conversions.semicircles_to_radians(0), 0)
    assert_equal(unit_conversions.semicircles_to_radians(1),
                 1.4629180792671596e-09)
    assert_equal(unit_conversions.semicircles_to_radians(1000),
                 1.4629180792671597e-06)
    assert_equal(unit_conversions.semicircles_to_radians(1000000000),
                 1.4629180792671597)
    assert_equal(unit_conversions.semicircles_to_radians(-1000000000),
                 -1.4629180792671597)


def test_convert_m_to_km():
    assert_equal(unit_conversions.convert_m_to_km(1054.3), 1.0543)


def test_minutes_from_start():
    timestamps = np.array([60.0, 120.0, 180.0])
    assert_array_almost_equal(
        unit_conversions.minutes_from_start(timestamps), [0, 1, 2])
