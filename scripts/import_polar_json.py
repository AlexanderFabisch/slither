"""Takes a data export from Polar flow and saves it in the database."""
from slither.service import Service
import sys


filenames = sys.argv[1:]
name_to_sport = {
    "Laufen": "running",
    "Radfahren": "cycling",
    "Rennrad": "racecycling",
    "Schwimmen": "swimming",
}

s = Service(base_path="tmp/data_import")
for filename in filenames:
    with open(filename, "r") as f:
        try:
            s.import_activity(f.read(), filename, name_to_sport=name_to_sport)
            print("Imported %s" % filename)
        except ValueError as e:
            print("Could not import %s" % filename)
            print(e)
