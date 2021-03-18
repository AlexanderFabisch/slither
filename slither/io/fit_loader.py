import time
import numpy as np
from slither.core.geodetic import compute_velocities
from slither.core.unit_conversions import semicircles_to_radians
from slither.domain_model import Activity
from fitparse import FitFile


class FitLoader:
    """Loads Flexible and Interoperable Data Transfer (FIT) files."""
    def __init__(self, filename):
        self.filename = filename

    def load(self):
        fitfile = FitFile(self.filename)
        records = list(fitfile.get_messages("record"))
        n_trackpoints = len(records)

        sport_messages = list(fitfile.get_messages("sport"))
        assert len(sport_messages) == 1
        sport = sport_messages[0].get_value("sport")

        activity_messages = list(fitfile.get_messages("activity"))
        assert len(activity_messages) == 1
        start_time = activity_messages[0].get_value("local_timestamp")
        total_timer_time = activity_messages[0].get_value("total_timer_time")

        session_messages = list(fitfile.get_messages("session"))
        assert len(session_messages) == 1
        distance = session_messages[0].get_value("total_distance")
        calories = session_messages[0].get_value("total_calories")
        heartrate = session_messages[0].get_value("avg_heart_rate")

        activity = Activity(
            sport=sport, start_time=start_time, time=total_timer_time,
            distance=distance, calories=calories, heartrate=heartrate,
            filetype="fit", has_path=n_trackpoints > 0)

        if activity.has_path:
            path = {
                "timestamps": np.empty(n_trackpoints),
                "coords": np.empty((n_trackpoints, 2)),
                "altitudes": np.empty(n_trackpoints),
                "heartrates": np.empty(n_trackpoints)
            }
            for k in path.keys():
                path[k][:] = np.nan

            for i, record in enumerate(records):
                record = record.get_values()
                path["timestamps"][i] = time.mktime(record["timestamp"].timetuple())
                if "position_lat" in record and "position_long" in record:
                    path["coords"][i] = record["position_lat"], record["position_long"]
                if "altitude" in record:
                    path["altitudes"][i] = record["altitude"]
                if "heart_rate" in record:
                    path["heartrates"][i] = record["heart_rate"]

            finite_coords = np.isfinite(path["coords"])
            path["coords"][finite_coords] = semicircles_to_radians(
                path["coords"][finite_coords])
            path["velocities"], _ = compute_velocities(
                path["timestamps"], path["coords"])

            activity.set_path(**path)

        return activity
