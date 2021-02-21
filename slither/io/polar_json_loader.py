import time
from datetime import datetime

import numpy as np
import json

from slither.geodetic import dist_on_earth
from slither.domain_model import Activity


SPORTS_MAPPING = {
    "RUNNING": "running",
    "CYCLING": "cycling",
    "ROAD_BIKING": "racecycling",
    "POOL_SWIMMING": "swimming",
    "OPEN_WATER_SWIMMING": "swimming",
    "OTHER_OUTDOOR": "other",
    "OTHER_INDOOR": "other",
}


class PolarJsonLoader:
    """Loads JSON files from Polar data export.

    You can export your personal data from Polar flow at

        https://account.polar.com/#export
    """
    def __init__(self, content):
        self.content = content
        self.training = None
        self.metadata = None

    def load(self):
        data = json.loads(self.content)
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
                timestamps.append(self._parse_timestamp(entry["dateTime"]))

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

        activity = Activity(
            sport=sport, start_time=start_time, distance=distance,
            time=duration, calories=calories, heartrate=heartrate,
            filetype=filetype, has_path=has_path)

        if has_path:
            path = self._compute(timestamps, lats, lons, alts, hrs)
            activity.set_path(**path)

        return activity

    def _parse_timestamp(self, t):
        date = datetime_from_str(t)
        return time.mktime(date.timetuple())

    def _compute(self, timestamps, latitudes, longitudes, altitudes, heartrates):
        result = {
            "timestamps": np.array(timestamps),
            "coords": np.deg2rad(np.column_stack((latitudes, longitudes))),
            "altitudes": np.array(altitudes),
            "heartrates": np.array(heartrates)
        }

        result["velocities"] = self._compute_velocities(
            result["timestamps"], result["coords"])
        return result

    def _compute_velocities(self, timestamps, coords):
        velocities = np.empty(len(timestamps))
        delta_t = np.diff(timestamps)
        for t in range(len(velocities)):
            if t == 0:
                velocity = 0.0
            else:
                dt = delta_t[t - 1]
                if dt <= 0.0:
                    velocity = velocities[t - 1]
                else:
                    dist = dist_on_earth(coords[t - 1, 0], coords[t - 1, 1],
                                         coords[t, 0], coords[t, 1])
                    velocity = dist / dt
            velocities[t] = velocity
        return velocities


def datetime_from_str(date_str):
    # e.g. 2021-01-30T13:24:11.000
    date_str = date_str[:-4]
    dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S")
    return dt
