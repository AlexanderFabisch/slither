"""Unit conversions."""
import numpy as np


def semicircles_to_radians(angles_in_semicircles):
    """Convert semicircles to radians.

    180 degrees correspond to 2 ** 31 semicircles. This unit is mostly
    used in Garmin systems or FIT files.

    Parameters
    ----------
    angles_in_semicircles : float or array
        Angle(s) in semicircles

    Returns
    -------
    angles_in_radians : float or array
        Angle(s) in radians
    """
    return np.deg2rad(angles_in_semicircles * (180.0 / (2 ** 31)))


def convert_m_to_km(distance_in_m):
    """Convert meters [m] to kilometers [km].

    Parameters
    ----------
    distance_in_m : float or array
        Distance in meters [m]

    Returns
    -------
    distance_in_km : float or array
        Distance in kilometers [km]
    """
    return distance_in_m / 1000.0


def convert_mps_to_kmph(velocity_in_mps):
    """Convert meters per second [m/s] to kilometers per hour [km/h].

    Parameters
    ----------
    velocity_in_mps : float or array
        Velocity in meters per second [m/s]

    Returns
    -------
    velocity_in_kmph : float or array
        Velocity in kilometers per hour [km/h]
    """
    return 3.6 * velocity_in_mps


def time_representation(hours, minutes, seconds):
    """Conversion of readable to internal time representation.

    Parameters
    ----------
    hours : float or array, shape (n_steps,)
        Hours since start

    minutes : float or array, shape (n_steps,)
        Minutes since start

    seconds : float or array, shape (n_steps,)
        Seconds since start

    Returns
    -------
    seconds : float or array-like, shape (n_steps,)
        Seconds since start
    """
    return hours * 3600.0 + minutes * 60 + seconds


def split_time(time):
    """Split time in seconds into hours, minutes, and seconds.

    Parameters
    ----------
    time : array, shape (n_steps,)
        Seconds since start

    Returns
    -------
    hours : array, shape (n_steps,)
        Hours since start

    minutes : array, shape (n_steps,)
        Minutes since start

    seconds : array, shape (n_steps,)
        Seconds since start
    """
    hours = time // 3600.0
    rest = time % 3600.0
    minutes = rest // 60.0
    seconds = rest % 60.0
    return hours, minutes, seconds


def minutes_from_start(timestamps):
    """Compute minutes from start of an array of timestamps.

    Parameters
    ----------
    timestamps : array-like, shape (n_steps,)
        Timestamps in ascending order (in seconds)

    Returns
    -------
    minutes : array, shape (n_steps,)
        Minutes since start
    """
    timestamps = np.copy(timestamps)
    timestamps -= timestamps[0]
    timestamps /= 60.0
    return timestamps
