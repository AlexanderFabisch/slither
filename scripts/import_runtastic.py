"""Takes a data export from Runtastic app and saves it in the database.

You can request a data export of Runtastic from their website at
account settings > data export. Then call this script with the path
to the training session data (folder 'Sport-sessions').
"""
import os
import glob
import json
import time
import datetime
import argparse
import rich
from rich.progress import Progress
from slither.io.gpx_loader import GpxLoader
from slither.domain_model import Activity
from slither.service import Service


parser = argparse.ArgumentParser(
    description="Import data exported from Runtastic.")
parser.add_argument(
    "filenames", type=str, nargs="+",
    help="Files (json) that should be imported.")
parser.add_argument(
    "--require_gpx", action="store_true",
    help="Require GPX file to import running or cycling activities.")
parser.add_argument(
    "--base_path", type=str, default=None,
    help="Base path in which data will be stored. "
         "This will be ~/.slither by default.")
args = parser.parse_args()

sport_id_to_name = {
    1: "running",
    3: "cycling",
    18: "swimming",
    19: "running",  # 'walking'
    22: "racecycling",
}

s = Service(base_path=args.base_path)

with Progress() as progress:
    task = progress.add_task("Data import", total=len(args.filenames))
    for filename in sorted(args.filenames):
        progress.console.print("Importing '%s'" % filename)
        progress.advance(task)
        with open(filename, "r") as f:
            content = f.read()
        session_data = json.loads(content)

        sport_id = int(session_data["sport_type_id"])
        if sport_id in sport_id_to_name:
            sport = sport_id_to_name[sport_id]
        else:
            sport = "other"
        try:
            calories = session_data["calories"]
        except KeyError:
            calories = 0
        distance = session_data["distance"]
        start_time = datetime.datetime.fromtimestamp(session_data["start_time"] / 1000.0)
        duration = session_data["duration"] / 1000.0

        close_activities = s.list_activity_for_date(start_time - datetime.timedelta(minutes=2))
        duplicate = False
        if close_activities:
            for a in close_activities:
                if abs(time.mktime(start_time.timetuple()) - time.mktime(a.start_time.timetuple())) < 60:
                    duplicate = True
                    break
        if duplicate:
            progress.console.print("[red]Found activity with similar start time, ignored.[/red]")
            rich.inspect(session_data)
            continue

        gpx_search_path = os.path.join(
            os.sep.join(filename.split(os.sep)[:-1]),
            "GPS-data", "*_%s.gpx" % session_data["id"])
        gpx_file = list(glob.glob(gpx_search_path))
        if len(gpx_file) == 0:
            if args.require_gpx and sport in ["running", "cycling", "racecycling"]:
                progress.console.print("[red]Activity has no GPX file, ignored.[/red]")
                continue
            activity = Activity(
                sport=sport, start_time=start_time, distance=distance,
                time=duration, calories=calories, has_path=False)
        else:
            gpx_file = gpx_file[0]
            with open(gpx_file, "r") as f:
                gpx_loader = GpxLoader(gpx_content=f.read())
                activity = gpx_loader.load()
            activity.start_time = start_time
            activity.sport = sport
            activity.calories = calories

        s.add_new_activity(activity)
