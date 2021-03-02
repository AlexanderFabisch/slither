"""Takes a batch of TCX files and stores them in the database."""
import argparse
from rich.progress import Progress
from slither.service import Service


parser = argparse.ArgumentParser(
    description="Import batch of TCX files.")
parser.add_argument(
    "filenames", type=str, nargs="+",
    help="Files (TCX) that should be imported.")
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
                s.import_activity(f.read(), filename)
            except ValueError:
                progress.console.print("Could not import %s" % filename)
