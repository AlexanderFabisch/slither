import numpy as np
from slither.gui.activity import check_coords
from slither.service import Service


import folium


def render_map(activity):
    path = activity.get_path()
    coords = np.rad2deg(check_coords(path["coords"]))
    distance_markers = activity.generate_distance_markers()
    valid_velocities = np.isfinite(path["velocities"])
    path["velocities"][np.logical_not(valid_velocities)] = 0.0

    center = np.mean(coords, axis=0)
    m = folium.Map(location=center)
    folium.Marker(
        coords[0].tolist(), tooltip="Start",
        icon=folium.Icon(color="red", icon="flag")).add_to(m)
    folium.Marker(
        coords[-1].tolist(), tooltip="Finish",
        icon=folium.Icon(color="green", icon="flag")).add_to(m)
    for label, marker in distance_markers.items():
        marker_location = coords[marker].tolist()
        folium.Marker(
            marker_location, tooltip=label,
            icon=folium.Icon(color="blue", icon="flag")).add_to(m)
    folium.PolyLine(coords).add_to(m)
    south_west = np.min(coords, axis=0).tolist()
    north_east = np.max(coords, axis=0).tolist()
    folium.FitBounds([south_west, north_east]).add_to(m)
    return m.get_root().render()


s = Service()
activities = s.list_activities()
a = [a for a in activities if a.has_path][0]
print(a.start_time)

m = render_map(a)
with open("map.html", "w") as f:
    f.write(m)
