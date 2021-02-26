import numpy as np
import jinja2
from datetime import datetime


class TcxExport:
    def __init__(self):
        pass

    def dumps(self, activity):
        env = jinja2.Environment(
            loader=jinja2.PackageLoader("slither", "resources"))
        env.filters["rad2deg"] = rad2deg
        env.filters["datetime_to_str"] = datetime_to_str
        env.filters["timestamp_to_str"] = timestamp_to_str
        template = env.get_template("export.tcx.template")
        return template.render(activity=activity)


def rad2deg(angle):  # handles None correctly
    if angle is None:
        return np.nan
    else:
        return np.rad2deg(angle)


def datetime_to_str(date):
    return date.strftime("%Y-%m-%dT%H:%M:%S.000Z")  # e.g. 2016-12-11T10:00:00.000Z


def timestamp_to_str(timestamp):
    date = datetime.fromtimestamp(timestamp)
    return datetime_to_str(date)
