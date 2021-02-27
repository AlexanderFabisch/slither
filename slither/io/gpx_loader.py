import time

import numpy as np
from bs4 import BeautifulSoup

from slither.io.utils import datetime_from_iso8601
from slither.ui_text import to_utf8
from slither.geodetic import compute_velocities
from slither.domain_model import Activity


class GpxLoader:
    """Loads GPS exchange format."""
    def __init__(self, gpx_content):
        self.content = to_utf8(gpx_content)
        self.training = None
        self.metadata = None

    def get_target_filename(self):
        return self._metadata()["filename"]

    def load(self):
        activity = Activity(**self._metadata())

        if activity.has_path:
            path, activity.distance, activity.time = self._compute()
            activity.set_path(**path)

        return activity

    def _metadata(self):
        if self.metadata is not None:
            return self.metadata

        if self.training is None:
            self.training = BeautifulSoup(self.content, "xml")

        gpx = self.training.find("gpx")
        if gpx is None:
            raise Exception("No 'gpx' tag found")
        metadata = gpx.find("metadata")
        start_time = datetime_from_iso8601(metadata.find("time").text)

        self.metadata = {
            "sport": "Other",  # not available in GPX
            "start_time": start_time,
            "filetype": "gpx",
            "has_path": True}
        return self.metadata

    def _compute(self):
        if self.training is None:
            self.training = BeautifulSoup(self.content, "xml")

        track = self.training.find("trk")
        if track is None:
            raise Exception("No 'trk' tag found")
        track_sequence = track.find("trkseg")
        if track_sequence is None:
            raise Exception("No 'trkseg' tag found")
        return self._parse_track_sequence(track_sequence)

    def _parse_track_sequence(self, track_sequence):
        trackpoints = track_sequence.findAll("trkpt")
        n_trackpoints = len(trackpoints)
        result = {
            "timestamps": np.empty(n_trackpoints),
            "coords": np.empty((n_trackpoints, 2)),
            "altitudes": np.empty(n_trackpoints),
            "heartrates": np.zeros(n_trackpoints)
        }

        for t, trackpoint in enumerate(trackpoints):
            result["timestamps"][t] = self._parse_timestamp(trackpoint)
            result["coords"][t] = self._parse_position(trackpoint)
            result["altitudes"][t] = self._parse_altitude(trackpoint)
            result["heartrates"][t] = float("nan")

        result["velocities"], distance = compute_velocities(
            result["timestamps"], result["coords"])
        time = result["timestamps"][-1] - result["timestamps"][0]
        return result, distance, time

    def _parse_timestamp(self, trackpoint):
        date = datetime_from_iso8601(trackpoint.find("time").text)
        return time.mktime(date.timetuple())

    def _parse_position(self, trackpoint):
        latitude = np.deg2rad(float(trackpoint["lat"]))
        longitude = np.deg2rad(float(trackpoint["lon"]))
        return latitude, longitude

    def _parse_altitude(self, trackpoint):
        elevation = float(trackpoint.find("ele").text)
        return elevation
