import sys
from slither.io.fit_loader import FitLoader


fit_loader = FitLoader(filename=sys.argv[-1])
activity = fit_loader.load()
print(activity)
