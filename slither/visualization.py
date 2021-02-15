import folium
import matplotlib
import numpy as np
from scipy.signal import medfilt

from slither.config import config
from slither.data_utils import check_coords, is_outlier, convert_mps_to_kmph


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
    plot(distances_in_km, altitudes)
    ax.set_xlim((0, total_distance_in_km))
    ax.set_ylim((min(altitudes), 1.1 * max(altitudes)))
    ax.set_xlabel("Distance [km]")
    ax.set_ylabel("Elevation [m]")


def plot(vel_axis, hr_axis, path):
    timestamps, velocities, heartrates = post_processing(path)

    matplotlib.rcParams["font.size"] = 10
    matplotlib.rcParams["legend.fontsize"] = 10

    handles = []
    labels = []

    n_steps = len(timestamps)

    vel_line, = vel_axis.plot(timestamps, velocities, color="#4f86f7",
                              alpha=0.8, lw=2)
    handles.append(vel_line)
    labels.append("Velocity")

    vel_axis.set_xlim((timestamps[0], timestamps[-1]))
    mean = np.nanmean(np.sort(velocities)[n_steps // 4:-n_steps // 4])
    vel_axis.set_ylim((0, 2 * mean))
    vel_axis.set_xlabel("Time [min]")
    vel_axis.set_ylabel("Velocity [km/h]")
    vel_axis.tick_params(axis="both", which="both", length=0)
    vel_axis.grid(True)

    if np.isfinite(heartrates).any():
        mean = np.nanmean(np.sort(heartrates)[n_steps // 4:-n_steps // 4])
        hr_line, = hr_axis.plot(timestamps, heartrates, color="#a61f34",
                                alpha=0.8, lw=2)
        handles.append(hr_line)
        labels.append("Heart Rate")

        hr_axis.set_ylim((0, 2 * mean))
        hr_axis.set_ylabel("Heart Rate [bpm]")
        hr_axis.tick_params(axis="both", which="both", length=0)
        hr_axis.spines["top"].set_visible(False)
    else:
        hr_axis.set_yticks(())
    hr_axis.grid(False)

    return handles, labels


def post_processing(path):
    timestamps = np.copy(path["timestamps"])
    timestamps -= timestamps[0]
    timestamps /= 60.0

    filter_width = config["plot"]["filter_width"]
    velocities = medfilt(path["velocities"], filter_width)
    velocities = convert_mps_to_kmph(velocities)

    heartrates = medfilt(path["heartrates"], filter_width)

    return timestamps, velocities, heartrates