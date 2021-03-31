import time
from datetime import datetime

import numpy as np
import json

from slither.core.geodetic import compute_velocities

SPORTS_MAPPING = {
    "RUNNING": "running",
    "CYCLING": "cycling",
    "ROAD_BIKING": "racecycling",
    "POOL_SWIMMING": "swimming",
    "OPEN_WATER_SWIMMING": "swimming",
    "OTHER_OUTDOOR": "other",
    "OTHER_INDOOR": "other",
}


def read_polar_json(content):
    """Read Polar's JSON format.

    You can export your personal data from Polar flow at

        https://account.polar.com/#export

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
    data = json.loads(content)
    start_time = datetime_from_str(data["startTime"])
    if "distance" in data:
        distance = data["distance"]
    else:
        distance = 0.0
    duration = float(data["duration"][2:-1])
    if "kiloCalories" in data:
        calories = data["kiloCalories"]
    else:
        calories = 0.0
    filetype = "json"
    assert len(data["exercises"]) == 1
    exercise = data["exercises"][0]
    if exercise["sport"] not in SPORTS_MAPPING:
        print("Unknown sport: '%s'" % data["name"])
        sport = "other"
    else:
        sport = SPORTS_MAPPING[exercise["sport"]]
    has_path = "recordedRoute" in exercise["samples"]
    if has_path:
        timestamps = []
        alts = []
        lons = []
        lats = []

        for entry in exercise["samples"]["recordedRoute"]:
            alts.append(entry["altitude"])
            lons.append(entry["longitude"])
            lats.append(entry["latitude"])
            timestamps.append(_parse_timestamp(entry["dateTime"]))

        hrs = [float("nan")] * len(alts)
        for idx, hr in enumerate(exercise["samples"]["heartRate"]):
            if idx >= len(hrs):
                print("More GPS samples than heartrate measurements")
                break
            if "value" in hr:
                hrs[idx] = hr["value"]

        if all(np.isnan(hrs)):
            heartrate = float("nan")
        else:
            heartrate = np.nanmean(hrs)
    else:
        heartrate = float("nan")

    metadata = dict(
        sport=sport, start_time=start_time, distance=distance,
        time=duration, calories=calories, heartrate=heartrate,
        filetype=filetype, has_path=has_path)

    if metadata["has_path"]:
        path = _make_path(timestamps, lats, lons, alts, hrs)
    else:
        path = None
    return metadata, path


def _parse_timestamp(t):
    date = datetime_from_str(t)
    return time.mktime(date.timetuple())


def _make_path(timestamps, latitudes, longitudes, altitudes, heartrates):
    result = {
        "timestamps": np.array(timestamps),
        "coords": np.deg2rad(np.column_stack((latitudes, longitudes))),
        "altitudes": np.array(altitudes),
        "heartrates": np.array(heartrates)
    }

    result["velocities"], _ = compute_velocities(
        result["timestamps"], result["coords"])
    return result


def datetime_from_str(date_str):
    # e.g. 2021-01-30T13:24:11.000
    date_str = date_str[:-4]
    dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
    return dt
