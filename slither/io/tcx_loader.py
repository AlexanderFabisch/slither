import time

import numpy as np
from bs4 import BeautifulSoup

from slither.io.utils import datetime_from_iso8601, to_utf8
from slither.core.geodetic import compute_velocities
from slither.domain_model import Activity


class TcxLoader:
    """Loads training center XML (TCX)."""
    def __init__(self, tcx_content):
        self.content = to_utf8(tcx_content)
        self.training = None
        self.metadata = None

    def get_target_filename(self):
        return self._metadata()["filename"]

    def load(self):
        activity = Activity(**self._metadata())

        if activity.has_path:
            path = self._compute()
            activity.set_path(**path)

        return activity

    def _metadata(self):
        if self.metadata is not None:
            return self.metadata

        if self.training is None:
            self.training = BeautifulSoup(self.content, "xml")

        training_center_database = self.training.find("TrainingCenterDatabase")
        if training_center_database is None:
            raise Exception("No 'TrainingCenterDatabase' tag found")
        activities = training_center_database.find("Activities").findAll(
            "Activity")
        assert len(activities) == 1
        activity = activities[0]

        sport = activity["Sport"].lower()

        calories, heartrates, start_time, times, total_dist = \
            self._parse_lap_metadata(activity)

        average_heartrate = np.sum(times * heartrates) / np.sum(times)

        has_path = activity.find("Trackpoint") is not None

        self.metadata = {
            "sport": sport,
            "start_time": start_time,
            "distance": total_dist,
            "time": sum(times),
            "calories": calories,
            "heartrate": average_heartrate,
            "filetype": "tcx",
            "has_path": has_path}
        return self.metadata

    def _parse_lap_metadata(self, activity):
        laps = activity.findAll("Lap")
        n_laps = len(laps)
        start_time = None
        total_dist = 0
        times = np.empty(n_laps)
        calories = 0
        heartrates = np.empty(n_laps)
        for i, lap in enumerate(laps):
            if start_time is None:
                start_time = datetime_from_iso8601(lap["StartTime"])
            total_dist += float(lap.find("DistanceMeters").text)
            times[i] = float(lap.find("TotalTimeSeconds").text)
            calories += float(lap.find("Calories").text)
            hr = lap.find("AverageHeartRateBpm")
            if hr is None:
                heartrates[i] = 0
            else:
                heartrates[i] = float(hr.text)
        return calories, heartrates, start_time, times, total_dist

    def _compute(self):
        if self.training is None:
            self.training = BeautifulSoup(self.content, "xml")

        training_center_database = self.training.find("TrainingCenterDatabase")
        if training_center_database is None:
            raise Exception("No 'TrainingCenterDatabase' tag found")
        return self._parse_activity(training_center_database)

    def _parse_activity(self, training_center_database):
        activities = training_center_database.find("Activities").findAll(
            "Activity")
        assert len(activities) == 1
        activity = activities[0]

        lap_infos = self._parse_laps(activity)
        if len(lap_infos) > 0:
            result = {k: np.concatenate([l[k] for l in lap_infos])
                      for k in lap_infos[0].keys()}
            return result
        else:
            return {}

    def _parse_laps(self, activity):
        laps = activity.findAll("Lap")
        lap_infos = []
        for lap in laps:
            tracks = lap.findAll("Track")
            if len(tracks) == 0:  # no GPS info
                continue
            for track in tracks:
                lap_info = self._parse_trackpoints(track)
                lap_infos.append(lap_info)
        return lap_infos

    def _parse_trackpoints(self, track):
        trackpoints = track.findAll("Trackpoint")
        n_trackpoints = len(trackpoints)
        result = {
            "timestamps": np.empty(n_trackpoints),
            "coords": np.empty((n_trackpoints, 2)),
            "altitudes": np.empty(n_trackpoints),
            "heartrates": np.empty(n_trackpoints)
        }

        for t, trackpoint in enumerate(trackpoints):
            result["timestamps"][t] = self._parse_timestamp(trackpoint)
            result["coords"][t] = self._parse_position(trackpoint)
            result["altitudes"][t] = self._parse_altitude(trackpoint)
            result["heartrates"][t] = self._parse_heartrate(trackpoint)

        result["velocities"], _ = compute_velocities(
            result["timestamps"], result["coords"])
        return result

    def _parse_heartrate(self, trackpoint):
        heartrate_tag = trackpoint.find("HeartRateBpm")
        if heartrate_tag is None:
            heartrate = float("nan")
        else:
            text = heartrate_tag.find("Value").text
            if text == "None":
                heartrate = float("nan")
            else:
                heartrate = float(text)
        return heartrate

    def _parse_altitude(self, trackpoint):
        altitude_meters = trackpoint.find("AltitudeMeters")
        if altitude_meters is None:
            altitude = 0.0
        else:
            try:
                altitude = float(altitude_meters.text)
            except ValueError:
                altitude = float("nan")
        return altitude

    def _parse_position(self, trackpoint):
        position = trackpoint.find("Position")
        if position is None:
            latitude = float("nan")
            longitude = float("nan")
        else:
            latitude_degrees = position.find("LatitudeDegrees")
            if latitude_degrees is None:
                latitude = float("nan")
            else:
                latitude = np.deg2rad(float(latitude_degrees.text))
            longitude_degrees = position.find("LongitudeDegrees")
            if longitude_degrees is None:
                longitude = float("nan")
            else:
                longitude = np.deg2rad(float(longitude_degrees.text))
        return latitude, longitude

    def _parse_timestamp(self, trackpoint):
        date = datetime_from_iso8601(trackpoint.find("Time").text)
        return time.mktime(date.timetuple())
