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


def compute_velocities(timestamps, coords):
    """Compute velocities from geodetic coordinates.

    Parameters
    ----------
    timestamps : array, shape (n_steps,)
        Timestamps

    coords : array, shape (n_steps, 2)
        Latitudes and longitudes in radians

    Returns
    -------
    velocities : array, shape (n_steps,)
        Velocities in meters per second

    total_distance : float
        Total distance in meters
    """
    delta_t = np.diff(timestamps)
    dists = dist_on_earth(
        coords[:-1, 0], coords[:-1, 1], coords[1:, 0], coords[1:, 1])

    n_steps = len(timestamps)
    velocities = np.empty(n_steps)
    velocities[0] = 0.0
    total_distance = 0.0

    for t in range(1, n_steps):
        dt = delta_t[t - 1]
        if dt <= 0.0:
            velocity = velocities[t - 1]
        else:
            velocity = dists[t - 1] / dt
            total_distance += dists[t - 1]
        velocities[t] = velocity
    return velocities, total_distance
