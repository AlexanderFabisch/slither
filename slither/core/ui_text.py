"""Text interface."""
import numpy as np
from slither.core.unit_conversions import split_time


class DataDisplay:  # TODO localization
    def __init__(self):
        pass  # TODO read some configuration

    def display_date(self, dt):
        return dt.strftime("%x")

    def display_datetime(self, dt):
        return dt.strftime("%Y/%m/%d %H:%M %a")

    def display_sport(self, sport):
        # TODO real localization
        return {"swimming": "Swimming",
                "running": "Running",
                "racecycling": "Bicycle Racing",
                "cycling": "Cycling",
                "other": "Other"}.get(sport, sport)

    def display_distance(self, distance):
        if distance == 0.0:
            return "-"
        if distance % 1000.0 == 0.0:
            return "%d km" % (distance / 1000.0)
        if distance < 2000.0:
            return "%d m" % np.round(distance, 0)
        return "%.2f km" % np.round(distance / 1000.0, 2)

    def display_time(self, time):
        if time == 0.0:
            return "-"
        if time is None or not np.isfinite(time):
            return "NA"

        if time < 60.0:
            return "%.2f s" % time

        hours, minutes, seconds = split_time(time)
        return "%02d:%02d:%02d h" % (hours, minutes, seconds)

    def display_calories(self, calories):
        if calories is None or calories == 0.0:
            return "-"
        return "%d kCal" % calories

    def display_heartrate(self, heartrate):
        if heartrate is None or heartrate == 0.0:
            return "-"
        return "%d bpm" % heartrate


d = DataDisplay()
