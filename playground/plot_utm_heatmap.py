import sys
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from matplotlib import ticker
import utm  # https://github.com/Turbo87/utm
from slither.service import Service
from slither.core.ui_text import convert_m_to_km
from scipy.stats import binned_statistic_2d


def all_trackpoints(lat_range, lon_range):
    s = Service()
    sql = "select latitude, longitude from trackpoints"
    df = pd.read_sql(sql, s.database.engine)
    df.latitude = np.rad2deg(df.latitude)
    df.longitude = np.rad2deg(df.longitude)
    df = df[df.latitude >= lat_range[0]]
    df = df[df.latitude <= lat_range[1]]
    df = df[df.longitude >= lon_range[0]]
    df = df[df.longitude <= lon_range[1]]
    df.dropna(inplace=True)
    return df.latitude.to_numpy(), df.longitude.to_numpy()


# Mallorca
lat_range = (38.0, 41.0)
lon_range = (1.0, 4.0)
# Bremen
#lat_range = (52.5, 53.5)
#lon_range = (8.5, 10.5)
# Harz
#lat_range = (51.4, 51.9)
#lon_range = (10.3, 11.3)

lats, lons = all_trackpoints(lat_range=lat_range, lon_range=lon_range)
eastings, northings, zone_number, zone_letter = utm.from_latlon(lats, lons)
eastings = convert_m_to_km(eastings)
northings = convert_m_to_km(northings)
print("Binning... ", end="")
sys.stdout.flush()
heatmap, xedge, yedge, binnumber = binned_statistic_2d(
    eastings, northings, np.ones_like(eastings), "count",
    bins=500)
print("Done.")

sns.set()
plt.figure(figsize=(6, 5))
Y, X = np.meshgrid(0.5 * (yedge[:-1] + yedge[1:]), 0.5 * (xedge[:-1] + xedge[1:]))
plt.contourf(X, Y, 1 + heatmap, locator=ticker.LogLocator())
plt.colorbar()
plt.title(f"UTM Zone {zone_number}{zone_letter}")
plt.xlabel("Easting [km]")
plt.ylabel("Northing [km]")
plt.tight_layout()
plt.show()
