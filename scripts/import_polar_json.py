"""Takes a data export from Polar flow and saves it in the database."""
import datetime
import time
import argparse
from rich.progress import Progress
from slither.service import Service
from slither.loader import PolarJsonLoader

parser = argparse.ArgumentParser(
    description="Import data exported from Polar.")
parser.add_argument(
    "filenames", type=str, nargs="+",
    help="Files (json) that should be imported.")
parser.add_argument(
    "--base_path", type=str, default=None,
    help="Base path in which data will be stored. "
         "This will be ~/.slither by default.")
args = parser.parse_args()

s = Service(base_path=args.base_path)

with Progress() as progress:
    task = progress.add_task("Data import", total=len(args.filenames))
    for filename in sorted(args.filenames):
        with open(filename, "r") as f:
            progress.console.print("Importing '%s'" % filename)
            progress.advance(task)
            try:
                loader = PolarJsonLoader(f.read())
                activity = loader.load()

                close_activities = s.list_activity_for_date(activity.start_time - datetime.timedelta(minutes=2))
                duplicate = False
                if close_activities:
                    for a in close_activities:
                        if abs(time.mktime(activity.start_time.timetuple()) - time.mktime(a.start_time.timetuple())) < 60:
                            duplicate = True
                            break
                if duplicate:
                    progress.console.print("[red]Found activity with similar start time, ignored.[/red]")
                    continue

                s.add_new_activity(activity)
            except ValueError as e:
                progress.console.print("[red]Could not import '%s'[/red]" % filename)
                progress.console.print(e)
