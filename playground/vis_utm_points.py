import numpy as np
import pandas as pd
import utm  # https://github.com/Turbo87/utm
from pytransform3d import visualizer
import open3d as o3d
from slither.service import Service
from slither.core.ui_text import convert_m_to_km


def all_trackpoints(lat_range, lon_range):
    s = Service()
    df = pd.read_sql_table(
        "trackpoints", s.database.engine,
        index_col="id", columns=["latitude", "longitude", "altitude"])
    df.latitude = np.rad2deg(df.latitude)
    df.longitude = np.rad2deg(df.longitude)
    df = df[df.latitude >= lat_range[0]]
    df = df[df.latitude <= lat_range[1]]
    df = df[df.longitude >= lon_range[0]]
    df = df[df.longitude <= lon_range[1]]
    df.dropna(inplace=True)
    return df.latitude.to_numpy(), df.longitude.to_numpy(), df.altitude.to_numpy()


alt_scale = 20.0
# Mallorca
lat_range = (38.0, 41.0)
lon_range = (1.0, 4.0)
# Bremen
#lat_range = (52.5, 53.5)
#lon_range = (8.5, 10.5)
# Harz
#lat_range = (51.4, 51.9)
#lon_range = (10.3, 11.3)
lats, lons, alts = all_trackpoints(lat_range, lon_range)
eastings, northings, zone_number, zone_letter = utm.from_latlon(lats, lons, force_zone_number=31, force_zone_letter="T")
eastings = convert_m_to_km(eastings)
northings = convert_m_to_km(northings)
alts = convert_m_to_km(alts)
alts *= alt_scale

fig = visualizer.figure()
fig.plot_transform(s=10)
pc = o3d.geometry.PointCloud()
points = np.hstack((eastings[:, np.newaxis], northings[:, np.newaxis], alts[:, np.newaxis]))
origin = np.min(points, axis=0)
points -= origin
pc.points = o3d.utility.Vector3dVector(points)
fig.add_geometry(pc)
fig.view_init()
fig.show()
