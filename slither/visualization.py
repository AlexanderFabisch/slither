import folium
import numpy as np

from slither.data_utils import check_coords, is_outlier


def render_map(activity):
    """Draw path on map with leaflet.js."""
    path = activity.get_path()
    coords = np.rad2deg(check_coords(path["coords"]))
    distance_markers = activity.generate_distance_markers()
    valid_velocities = np.isfinite(path["velocities"])
    path["velocities"][np.logical_not(valid_velocities)] = 0.0
    # TODO find a way to colorize path according to velocities

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


def plot_velocities(activity, ax):
    path = activity.get_path()
    velocities = path["velocities"][1:]
    finite_velocities = np.isfinite(velocities)
    velocities = velocities[finite_velocities]
    no_outlier = np.logical_not(is_outlier(velocities))
    velocities = velocities[no_outlier] * 3.6
    dt = np.diff(path["timestamps"])[finite_velocities][no_outlier]

    ax.hist(velocities, bins=50, weights=dt)
    ax.set_xlabel("Velocity [km/h]")
    ax.set_ylabel("Percentage")
    ax.set_yticks(())


def plot_elevation(path, ax):
    dts = np.diff(path["timestamps"])
    velocities = path["velocities"][:-1]
    altitudes = path["altitudes"][:-1]

    valid_data = np.isfinite(velocities)
    dts = dts[valid_data]
    velocities = velocities[valid_data]
    altitudes = altitudes[valid_data]
    distances_in_m = np.cumsum(dts * velocities)
    distances_in_km = distances_in_m / 1000.0
    total_distance_in_m = np.nanmax(distances_in_m)
    total_distance_in_km = np.nanmax(distances_in_km)

    # TODO exactly 0 seems to be an indicator for an error, a better method would be to detect jumps
    valid_data = np.logical_and(np.isfinite(altitudes), altitudes != 0.0)
    distances_in_km = distances_in_km[valid_data]
    altitudes = altitudes[valid_data]

    altitude_diffs = np.diff(altitudes)
    up = sum(altitude_diffs[altitude_diffs > 0])
    down = -sum(altitude_diffs[altitude_diffs < 0])
    slope_in_percent = 100.0 * up / total_distance_in_m

    ax.set_title(f"Elevation gain: {int(np.round(up, 0))} m, elevation loss: {int(np.round(down, 0))} m, "
                 f"slope {np.round(slope_in_percent, 2)} %")
    ax.fill_between(distances_in_km, np.zeros_like(altitudes), altitudes, alpha=0.3)
    ax.plot(distances_in_km, altitudes)
    ax.set_xlim((0, total_distance_in_km))
    ax.set_ylim((min(altitudes), 1.1 * max(altitudes)))
    ax.set_xlabel("Distance [km]")
    ax.set_ylabel("Elevation [m]")
