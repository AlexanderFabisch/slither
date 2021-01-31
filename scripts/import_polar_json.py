"""Takes a batch of TCX files and stores them in the database."""
from slither.service import Service
import sys


filenames = sys.argv[1:]

s = Service()
for filename in filenames:
    with open(filename, "r") as f:
        try:
            s.import_activity(f.read(), filename)
            print("Imported %s" % filename)
        except ValueError:
            print("Could not import %s" % filename)