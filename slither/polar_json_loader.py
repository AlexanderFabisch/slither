import time
from datetime import datetime

import numpy as np
import json

from .data_utils import dist_on_earth
from .domain_model import Activity


class PolarJsonLoader:
    """Loads JSON files from Polar data export.

    You can export your personal data from Polar flow at

        https://account.polar.com/#export
    """
    def __init__(self, content, name_to_sport={}):
        self.content = content
        self.training = None
        self.metadata = None
        self.name_to_sport = name_to_sport

    def get_target_filename(self):
        return self._metadata()["filename"]

    def load(self):
        data = json.loads(self.content)
        if data["name"] in self.name_to_sport:
            sport = self.name_to_sport[data["name"]]
        else:
            print("Unknown sport: '%s'" % data["name"])
            sport = "other"
        start_time = datetime_from_str(data["startTime"])
        if "distance" in data:
            distance = data["distance"]
        else:
            distance = 0.0
        duration = float(data["duration"][2:-1])  # TODO correct unit?
        if "kiloCalories" in data:
            calories = data["kiloCalories"]
        else:
            calories = 0.0
        filetype = "json"
        assert len(data["exercises"]) == 1
        exercise = data["exercises"][0]
        has_path = "recordedRoute" in exercise["samples"]
        if has_path:
            timestamps = []
            alts = []
            lons = []
            lats = []
            # TODO use correct timestamps for gps and heartrate
            #print(len(exercise["samples"]["recordedRoute"]))
            #print(len(exercise["samples"]["heartRate"]))
            for entry in exercise["samples"]["recordedRoute"]:
                alts.append(entry["altitude"])
                lons.append(entry["longitude"])
                lats.append(entry["latitude"])
                timestamps.append(self._parse_timestamp(entry["dateTime"]))
            hrs = [float("nan")] * len(alts)
            for idx, hr in enumerate(exercise["samples"]["heartRate"]):
                if idx >= len(hrs):
                    break
                if "value" in hr:
                    hrs[idx] = hr["value"]
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
            "heartrates": np.array(heartrates)  # TODO missing heartrates?
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
