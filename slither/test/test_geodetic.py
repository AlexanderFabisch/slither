import numpy as np
from slither.core.geodetic import haversine_dist, dist_on_earth
from nose.tools import assert_less


def test_compare_haversine_pyproj():
    lat_roland, long_roland = np.deg2rad([53.0759, 8.80731])
    lat_sol, long_sol = np.deg2rad([40.689249, -74.0445])
    hdistance = haversine_dist(lat_roland, long_roland, lat_sol, long_sol)
    distance = dist_on_earth(lat_roland, long_roland, lat_sol, long_sol)
    difference = abs(hdistance - distance)
    relative_difference = difference / distance
    assert_less(relative_difference, 0.003)
