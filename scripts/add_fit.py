"""Takes a batch of FIT files and stores them in the database."""
import argparse
from rich.progress import Progress
from slither.service import Service
from slither.loader import FitLoader


parser = argparse.ArgumentParser(
    description="Import batch of FIT files.")
parser.add_argument(
    "filenames", type=str, nargs="+",
    help="Files (FIT) that should be imported.")
parser.add_argument(
    "--base_path", type=str, default=None,
    help="Base path in which data will be stored. "
         "This will be ~/.slither by default.")
args = parser.parse_args()


s = Service(base_path=args.base_path)
with Progress() as progress:
    task = progress.add_task("Data import", total=len(args.filenames))
    for filename in args.filenames:
        progress.console.print("Importing '%s'" % filename)
        progress.advance(task)
        with open(filename, "r") as f:
            try:
                fit_loader = FitLoader(filename=filename)
                activity = fit_loader.load()
                s.add_new_activity(activity)
            except ValueError:
                progress.console.print("Could not import %s" % filename)
