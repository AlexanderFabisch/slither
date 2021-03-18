from slither.core import unit_conversions
from nose.tools import assert_equal


def test_semicircles_to_radians():
    assert_equal(unit_conversions.semicircles_to_radians(0), 0)
    assert_equal(unit_conversions.semicircles_to_radians(1), 1.4629180792671596e-09)
    assert_equal(unit_conversions.semicircles_to_radians(1000), 1.4629180792671597e-06)
    assert_equal(unit_conversions.semicircles_to_radians(1000000000), 1.4629180792671597)
    assert_equal(unit_conversions.semicircles_to_radians(-1000000000), -1.4629180792671597)
