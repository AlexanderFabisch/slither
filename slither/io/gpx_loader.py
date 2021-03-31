import time

import numpy as np
from bs4 import BeautifulSoup

from slither.io.utils import datetime_from_iso8601
from slither.core.geodetic import compute_velocities


def read_gpx(content):
    """Read GPS exchange format file (GPX).

    Parameters
    ----------
    content : str
        File content

    Returns
    -------
    metadata : dict
        Activity metadata

    path : dict
        Trackpoint data
    """
    training = BeautifulSoup(content, "xml")

    metadata = _metadata(training)

    if metadata["has_path"]:
        path, metadata["distance"], metadata["time"] = _parse_training(training)
    else:
        path = None
        metadata["distance"] = 0.0
        metadata["time"] = 0.0

    return metadata, path


def _metadata(training):
    gpx = training.find("gpx")
    if gpx is None:
        raise Exception("No 'gpx' tag found")
    metadata = gpx.find("metadata")
    start_time = datetime_from_iso8601(metadata.find("time").text)

    metadata = {
        "sport": "Other",  # not available in GPX
        "start_time": start_time,
        "filetype": "gpx",
        "has_path": True}
    return metadata


def _parse_training(training):
    track = training.find("trk")
    if track is None:
        raise Exception("No 'trk' tag found")
    track_sequence = track.find("trkseg")
    if track_sequence is None:
        raise Exception("No 'trkseg' tag found")
    return _parse_track_sequence(track_sequence)


def _parse_track_sequence(track_sequence):
    trackpoints = track_sequence.findAll("trkpt")
    n_trackpoints = len(trackpoints)
    result = {
        "timestamps": np.empty(n_trackpoints),
        "coords": np.empty((n_trackpoints, 2)),
        "altitudes": np.empty(n_trackpoints),
        "heartrates": np.zeros(n_trackpoints)
    }

    for t, trackpoint in enumerate(trackpoints):
        result["timestamps"][t] = _parse_timestamp(trackpoint)
        result["coords"][t] = _parse_position(trackpoint)
        result["altitudes"][t] = _parse_altitude(trackpoint)
        result["heartrates"][t] = float("nan")

    result["velocities"], distance = compute_velocities(
        result["timestamps"], result["coords"])
    time = result["timestamps"][-1] - result["timestamps"][0]
    return result, distance, time


def _parse_timestamp(trackpoint):
    date = datetime_from_iso8601(trackpoint.find("time").text)
    return time.mktime(date.timetuple())


def _parse_position(trackpoint):
    latitude = np.deg2rad(float(trackpoint["lat"]))
    longitude = np.deg2rad(float(trackpoint["lon"]))
    return latitude, longitude


def _parse_altitude(trackpoint):
    elevation = float(trackpoint.find("ele").text)
    return elevation
