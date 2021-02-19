import sys
import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib import ticker
from slither.service import Service
from slither.domain_model import Trackpoint
from scipy.stats import binned_statistic_2d


def all_trackpoints():
    s = Service(base_path="tmp/data_import/")
    print("Loading trackpoints... ", end="")
    sys.stdout.flush()
    trackpoints = s.database.session.query(Trackpoint).all()
    print("Done.")

    print("Extracting lats ands lons... ", end="")
    sys.stdout.flush()
    latitudes = np.array([t.latitude for t in trackpoints], dtype=np.float)
    longitudes = np.array([t.longitude for t in trackpoints], dtype=np.float)
    print("Done.")
    return latitudes, longitudes


#range = ((53.08, 53.12), (8.81, 8.84))
range = ((53.0, 53.15), (8.75, 8.9))
#range = ((52.9, 53.4), (8.55, 9.05))
#range = ((52.2, 53.7), (8.0, 9.5))
#range = ((47.0, 55.0), (5.5, 15.5))

lats, lons = all_trackpoints()
print("Radian to degrees... ", end="")
sys.stdout.flush()
lats = np.rad2deg(lats)
lons = np.rad2deg(lons)
print("Done.")
# TODO lats + longs to Cartesian coordinates
print("Binning... ", end="")
sys.stdout.flush()
heatmap, xedge, yedge, binnumber = binned_statistic_2d(
    lats, lons, np.ones_like(lats), "count",
    bins=500, range=range)
print("Done.")

sns.set()
plt.figure(figsize=(6, 5))
Y, X = np.meshgrid(0.5 * (yedge[:-1] + yedge[1:]), 0.5 * (xedge[:-1] + xedge[1:]))
plt.contourf(Y, X, 1 + heatmap, locator=ticker.LogLocator())
plt.colorbar()
plt.tight_layout()
plt.show()
