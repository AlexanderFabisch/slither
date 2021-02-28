import numpy as np
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib import ticker
from slither.service import Service
from scipy.stats import binned_statistic_2d


def all_trackpoints():
    s = Service()
    sql = "select latitude, longitude from trackpoints"
    df = pd.read_sql(sql, s.database.engine)
    df.latitude = np.rad2deg(df.latitude)
    df.longitude = np.rad2deg(df.longitude)
    df.dropna(inplace=True)
    return df.latitude.to_numpy(), df.longitude.to_numpy()


#range = ((53.08, 53.12), (8.81, 8.84))
#range = ((53.0, 53.15), (8.75, 8.9))
#range = ((52.9, 53.4), (8.55, 9.05))
#range = ((52.2, 53.7), (8.0, 9.5))
#range = ((47.0, 55.0), (5.5, 15.5))
range = ((39.3, 40.1), (2.35, 3.15))

lats, lons = all_trackpoints()
heatmap, xedge, yedge, binnumber = binned_statistic_2d(
    lats, lons, np.ones_like(lats), "count",
    bins=500, range=range)

sns.set()
plt.figure(figsize=(6, 5))
Y, X = np.meshgrid(0.5 * (yedge[:-1] + yedge[1:]), 0.5 * (xedge[:-1] + xedge[1:]))
plt.contourf(Y, X, 1 + heatmap, locator=ticker.LogLocator())
plt.colorbar()
plt.title("Heatmap")
plt.xlabel("Longitude [deg]")
plt.ylabel("Latitude [deg]")
plt.tight_layout()
plt.show()
