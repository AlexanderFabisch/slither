"""Takes a data export from Runtastic app and saves it in the database.

You can request a data export of Runtastic from their website at
account settings > data export. Then call this script with the path
to the training session data (folder 'Sport-sessions').
"""
import os
import sys
import glob
import json
import datetime
from slither.gpx_loader import GpxLoader
from slither.domain_model import Activity
from slither.service import Service


sport_mapping = {
    1: "running",
    3: "cycling",
    18: "swimming",
    19: "running",  # 'walking'
    22: "racecycling",
}

s = Service(base_path="tmp/data_import")

path = sys.argv[-1]
filenames = sorted(glob.glob(os.path.join(path, "*.json")))
for filename in filenames:
    with open(filename, "r") as f:
        content = f.read()
        session_data = json.loads(content)

        sport_id = int(session_data["sport_type_id"])
        if sport_id in sport_mapping:
            sport = sport_mapping[sport_id]
        else:
            sport = "other"
        try:
            calories = session_data["calories"]
        except KeyError:
            calories = 0
        distance = session_data["distance"]
        start_time = datetime.datetime.fromtimestamp(session_data["start_time"] / 1000.0)
        time = session_data["duration"] / 1000.0

        gpx_search_path = os.path.join(os.sep.join(filename.split(os.sep)[:-1]), "GPS-data", "*_%s.gpx" % session_data["id"])
        gpx_file = list(glob.glob(gpx_search_path))
        if len(gpx_file) == 0:
            activity = Activity(sport=sport, start_time=start_time, distance=distance, time=time, calories=calories, has_path=False)
        else:
            gpx_file = gpx_file[0]
            with open(gpx_file, "r") as f:
                gpx_loader = GpxLoader(gpx_content=f.read())
                activity = gpx_loader.load()
            activity.sport = sport
            activity.calories = calories

        s.add_new_activity(activity)
        print("Imported %s" % filename)
