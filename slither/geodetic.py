import numpy as np
import pyproj


def haversine_dist(lat1, long1, lat2, long2, earth_radius=6371000.0):
    """Haversine distance between two positions on earth.

    This is a simple approximation. A better way is to use pyproj,
    which uses a WGS84 model of the earth.

    Parameters
    ----------
    lat1 : array-like or float
        latitude of position 1 in radians

    long1 : array-like or float
        longitude of position 1 in radians

    lat2 : array-like or float
        latitude of position 2 in radians

    long2 : array-like or float
        longitude of position 2 in radians

    earth_radius : float
        average radius of the earth in meters, should be between
        6353000 and 6384000

    Returns
    -------
    distance : float
        Distance between two positions on the surface of the earth in meters
    """
    lat_dist = lat2 - lat1
    long_dist = long2 - long1
    a = (np.sin(0.5 * lat_dist) ** 2 +
         np.cos(lat1) * np.cos(lat2) * np.sin(0.5 * long_dist) ** 2)
    angular_dist = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    return earth_radius * angular_dist


class PyprojDist:
    def __init__(self):
        self.geod = pyproj.Geod(ellps="WGS84")

    def __call__(self, lat1, long1, lat2, long2):
        """Compute distance between two positions on earth.

        Parameters
        ----------
        lat1 : array-like or float
            latitude of position 1 in radians

        long1 : array-like or float
            longitude of position 1 in radians

        lat2 : array-like or float
            latitude of position 2 in radians

        long2 : array-like or float
            longitude of position 2 in radians

        Returns
        -------
        distance : float
            Distance between two positions on the surface of the earth in meters
        """
        _, _, dist = self.geod.inv(long1, lat1, long2, lat2, radians=True)
        return dist


dist_on_earth = PyprojDist()
