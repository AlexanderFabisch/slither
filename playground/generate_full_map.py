import folium
import numpy as np
from slither.service import Service
from slither.domain_model import Trackpoint
from slither.core.analysis import check_coords


def all_trackpoints():
    s = Service()
    trackpoints = s.database.session.query(Trackpoint).all()
    timestamps = np.array([t.timestamp for t in trackpoints])

    coords = np.array([(t.latitude, t.longitude) for t in trackpoints],
                      dtype=float)
    split_indices = np.where(np.abs(np.diff(timestamps)) > 100.0)[0]
    coords = np.array_split(coords, split_indices + 1)

    new_coords = []
    for path in coords:
        c = np.rad2deg(check_coords(path))
        if len(c) < 2:
            continue
        new_coords.append(c)
    return new_coords


def render_map(all_coords):
    """Draw path on map with leaflet.js."""
    m = folium.Map(location=all_coords[-1][-1])
    for coords in all_coords:
        folium.PolyLine(coords).add_to(m)
    return m


coords = all_trackpoints()
m = render_map(coords)
m.save("index.html")
