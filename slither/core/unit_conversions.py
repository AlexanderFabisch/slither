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


def convert_m_to_km(distance):
    """Convert meters [m] to kilometers [km]."""
    return distance / 1000.0


def convert_mps_to_kmph(velocity):
    """Convert meters per second [m/s] to kilometers per hour [km/h]."""
    return 3.6 * velocity


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
    """Compute minutes from start of an array of timestamps in seconds.

    Parameters
    ----------
    timestamps : array-like, shape (n_steps,)
        Timestamps in ascending order

    Returns
    -------
    seconds : array, shape (n_steps,)
        Seconds since start
    """
    timestamps = np.copy(timestamps)
    timestamps -= timestamps[0]
    timestamps /= 60.0
    return timestamps
