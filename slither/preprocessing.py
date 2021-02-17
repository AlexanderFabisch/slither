import numpy as np
import pyproj
from scipy.signal import medfilt

from slither.data_utils import convert_mps_to_kmph


def check_coords(coords):
    """Filter non-finite GPS coordinates."""
    coords_sum = coords[:, 0] + coords[:, 1]
    valid_coords = np.isfinite(coords_sum)
    return coords[valid_coords]


def is_outlier(points, thresh=3.5):
    """Check an array for outliers.

    Parameters:
    -----------
    points : array-like, shape (n_samples, n_dims)
        An array of observations

    thresh : float
        The modified z-score to use as a threshold. Observations with
        a modified z-score (based on the median absolute deviation) greater
        than this value will be classified as outliers.

    Returns:
    --------
    mask : array-like, shape (n_samples,)
        A boolean array that indicates whether the corresponding sample is an
        outlier

    References:
    ----------
    http://stackoverflow.com/a/22357811/915743

    Boris Iglewicz and David Hoaglin (1993), "Volume 16: How to Detect and
    Handle Outliers", The ASQC Basic References in Quality Control:
    Statistical Techniques, Edward F. Mykytka, Ph.D., Editor.
    """
    points = np.asarray(points)
    if points.ndim == 1:
        points = points[:, np.newaxis]

    nonzero = np.unique(np.nonzero(points)[0])
    median = np.median(points[nonzero], axis=0)
    diff = np.sum((points - median) ** 2, axis=-1)
    diff = np.sqrt(diff)
    med_abs_deviation = np.median(diff[nonzero])

    modified_z_score = 0.6745 * diff / med_abs_deviation

    return modified_z_score > thresh


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


def filtered_heartrates(path, filter_width):
    return medfilt(path["heartrates"], filter_width)


def filtered_velocities_in_kmph(path, filter_width):
    velocities = medfilt(path["velocities"], filter_width)
    return convert_mps_to_kmph(velocities)