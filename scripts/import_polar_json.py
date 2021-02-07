"""Takes a data export from Polar flow and saves it in the database."""
import sys
from slither.service import Service
from slither.polar_json_loader import PolarJsonLoader


filenames = sys.argv[1:]

s = Service(base_path="tmp/data_import")
for filename in filenames:
    with open(filename, "r") as f:
        try:
            loader = PolarJsonLoader(f.read())
            activity = loader.load()
            s.add_new_activity(activity)
            print("Imported %s" % filename)
        except ValueError as e:
            print("Could not import %s" % filename)
            print(e)
