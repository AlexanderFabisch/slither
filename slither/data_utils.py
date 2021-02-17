import numpy as np


def convert_mps_to_kmph(velocity):
    """Convert meters per second to kilometers per hour."""
    return 3.6 * velocity


def time_representation(hours, minutes, seconds):
    """Conversion to internal time representation."""
    return hours * 3600.0 + minutes * 60 + seconds


def split_time(time):
    """Split time in seconds into hours, minutes, and seconds."""
    hours = time // 3600.0
    rest = time % 3600.0
    minutes = rest // 60.0
    seconds = rest % 60.0
    return hours, minutes, seconds


def appropriate_partition(distance):
    """Find appropriate partition of a distance into parts."""
    if distance < 5000:
        return 400
    elif distance < 20000:
        return 1000
    elif distance < 40000:
        return 2000
    elif distance < 100000:
        return 5000
    else:
        return 10000


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
        elif distance % 1000.0 == 0.0:
            return "%d km" % (distance / 1000.0)
        elif distance < 2000.0:
            return "%d m" % np.round(distance, 0)
        else:
            return "%.2f km" % np.round(distance / 1000.0, 2)

    def display_time(self, time):
        if time == 0.0:
            return "-"
        if time is None or not np.isfinite(time):
            return "NA"

        if time < 60.0:
            return "%.2f s" % time
        else:
            hours, minutes, seconds = split_time(time)
            return "%02d:%02d:%02d h" % (hours, minutes, seconds)

    def display_calories(self, calories):
        if calories is None or calories == 0.0:
            return "-"
        else:
            return "%d kCal" % calories

    def display_heartrate(self, heartrate):
        if heartrate is None or heartrate == 0.0:
            return "-"
        else:
            return "%d bpm" % heartrate


d = DataDisplay()


def to_utf8(content):
    try:
        content = content.decode("windows-1252")
    finally:
        return content.encode("utf-8")
