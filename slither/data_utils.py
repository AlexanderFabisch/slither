import numpy as np


def convert_mps_to_kmph(velocity):
    """Convert meters per second to kilometers per hour."""
    return 3.6 * velocity


def time_representation(hours, minutes, seconds):
    """Conversion to internal time representation."""
    return hours * 3600.0 + minutes * 60 + seconds


try:
    import pyproj

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
except ImportError:
    import warnings


    warnings.warn("pyproj not available, falling back to haversine distance")


    def haversine_dist(lat1, long1, lat2, long2, earth_radius=6371000.0):
        """Haversine distance between two positions on earth.

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


    dist_on_earth = haversine_dist


def check_coords(coords):
    """Filter invalid coordinates."""
    coords_sum = coords[:, 0] + coords[:, 1]
    valid_coords = np.isfinite(coords_sum)
    return coords[valid_coords]


def appropriate_partition(distance):
    if distance < 5000:
        return 400
    elif distance < 20000:
        return 1000
    elif distance < 40000:
        return 2000
    elif distance < 100000:
        return 5000
    else:
        return 10000


def split_time(time):  # TODO refactor
    hours = time // 3600.0
    rest = time % 3600.0
    minutes = rest // 60.0
    seconds = rest % 60.0
    return hours, minutes, seconds


class DataDisplay:  # TODO localization
    def __init__(self):
        pass  # TODO read some configuration

    def display_date(self, dt):
        return dt.strftime("%x")

    def display_datetime(self, dt):
        return dt.strftime("%Y/%m/%d %H:%M %a")

    def display_sport(self, sport):
        # TODO real localization
        return {"swimming": "Swimming",
                "running": "Running",
                "racecycling": "Bicycle Racing",
                "cycling": "Cycling",
                "other": "Other"}.get(sport, sport)

    def display_distance(self, distance):
        if distance == 0.0:
            return "-"
        elif distance % 1000.0 == 0.0:
            return "%d km" % (distance / 1000.0)
        elif distance < 2000.0:
            return "%d m" % np.round(distance, 0)
        else:
            return "%.2f km" % np.round(distance / 1000.0, 2)

    def display_time(self, time):
        if time  == 0.0:
            return "-"
        if time is None or not np.isfinite(time):
            return "NA"

        if time < 60.0:
            return "%.2f s" % time
        else:
            hours, minutes, seconds = split_time(time)
            return "%02d:%02d:%02d h" % (hours, minutes, seconds)

    def display_calories(self, calories):
        if calories is None or calories == 0.0:
            return "-"
        else:
            return "%d kCal" % calories

    def display_heartrate(self, heartrate):
        if heartrate is None or heartrate == 0.0:
            return "-"
        else:
            return "%d bpm" % heartrate


d = DataDisplay()


def to_utf8(content):
    try:
        content = content.decode("windows-1252")
    finally:
        return content.encode("utf-8")


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