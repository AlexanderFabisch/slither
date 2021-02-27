from collections import deque

import numpy as np
from scipy.signal import medfilt

from slither.ui_text import convert_mps_to_kmph
from slither.config import config


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


def filtered_heartrates(path, filter_width):
    return medfilt(path["heartrates"], filter_width)


def filtered_velocities_in_kmph(path, filter_width):
    velocities = medfilt(path["velocities"], filter_width)
    velocities = np.convolve(
        velocities, np.ones(filter_width) / filter_width,
        mode="same")
    return convert_mps_to_kmph(velocities)


def elevation_summary(altitudes, total_distance_in_m):
    """Overall elevation statistics.

    Parameters
    ----------
    altitudes : array, shape (n_steps,)
        Altitudes

    total_distance_in_m : float
        Total distance in meters

    Returns
    -------
    gain : float
        Total elevation gain

    loss : float
        Total elevation loss

    slope_in_percent : float
        Average slope in percent, ignoring elevation loss
    """
    altitude_diffs = np.diff(altitudes)
    gain = sum(altitude_diffs[altitude_diffs > 0])
    loss = -sum(altitude_diffs[altitude_diffs < 0])
    slope_in_percent = 100.0 * gain / total_distance_in_m
    return gain, loss, slope_in_percent


def get_paces(activity):
    """Generate pace table of an activity.

    Parameters
    ----------
    activity : Activity
        Activity

    Returns
    -------
    paces : list
        Each entry is a tuple of the traveled distance in meters and
        corresponding average pace at this distance in seconds per
        kilometer.
    """
    path = activity.get_path()
    velocities = path["velocities"][1:]
    timestamps = path["timestamps"]
    delta_t = np.diff(timestamps)

    max_velocity = config["max_velocity"].get(
        activity.sport, config["max_velocity"]["default"])
    valid_velocities = np.where(velocities <= max_velocity)
    velocities = velocities[valid_velocities]
    delta_t = delta_t[valid_velocities]

    dist = np.cumsum(velocities * delta_t)
    split_distance = appropriate_partition(dist[-1])

    pdt = config["pace_distance_table"]
    pace_distance = pdt.get(activity.sport, pdt["other"])

    paces = []
    last_t = 0
    for threshold in range(split_distance, int(dist[-1]), split_distance):
        t = np.argmax(dist >= threshold)
        split_time = timestamps[t] - timestamps[last_t]
        pace = split_time / split_distance * pace_distance
        paces.append((threshold, pace))
        last_t = t
    return paces


def fastest_part(sport, timestamps, velocities, distance):
    """Compute fastest time for a given distance in an activity.

    Parameters
    ----------
    sport : str
        Sport

    timestamps : array, shape (n_steps,)
        Timestamps

    velocities : array, shape (n_steps,)
        Velocities

    distance : float
        Length of the segment for which we want to compute the fastest time
        in this activity.

    Returns
    -------
    record : float
        Fastest time for the requested distance in seconds
    """
    queue_dist = 0.0
    queue_time = 0.0
    dqueue = deque()
    tqueue = deque()

    v = velocities[1:]
    dt = np.diff(timestamps)
    record = float("inf")

    for t in range(len(v)):
        if np.isnan(v[t]):
            queue_dist = 0.0
            queue_time = 0.0
            dqueue.clear()
            tqueue.clear()
            continue
        if v[t] > config["max_velocity"][sport]:
            continue
        dist = v[t] * dt[t]
        dqueue.appendleft(dist)
        tqueue.appendleft(dt[t])
        queue_dist += dist
        queue_time += dt[t]
        while queue_dist > distance:
            if queue_time < record:
                record = queue_time
            dist = dqueue.pop()
            time = tqueue.pop()
            queue_dist -= dist
            queue_time -= time

    return record


def appropriate_partition(distance):
    """Find appropriate partition of a distance into parts.

    Parameters
    ----------
    distance : float
        Traveled distance in meters

    Returns
    -------
    segment_distance : float
        Appropriate length of segments in which we split the total distance
    """
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


def compute_distances_for_valid_trackpoints(path):
    """Compute distances for valid trackpoints from a path.

    Parameters
    ----------
    path : dict
        A path that has at lest the entries 'timestamps' and 'velocities'.

    Returns
    -------
    distances_in_m : array, shape (n_valid_trackpoints,)
        Distances in meters [m] per valid trackpoint.

    valid_trackpoints : array, shape (n_valid_trackpoints,)
        Indices of finite velocities in path.
    """
    delta_ts = np.gradient(path["timestamps"])
    velocities = path["velocities"]

    valid_trackpoints = np.isfinite(velocities)
    delta_ts = delta_ts[valid_trackpoints]
    velocities = velocities[valid_trackpoints]

    distances_in_m = np.cumsum(delta_ts * velocities)
    return distances_in_m, valid_trackpoints
