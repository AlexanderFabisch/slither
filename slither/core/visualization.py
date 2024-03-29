"""Visualization of training data."""
import folium
import matplotlib
import numpy as np

from .config import config
from .analysis import (
    is_outlier, check_coords, filtered_heartrates, elevation_summary,
    filter_median_average, appropriate_partition,
    compute_distances_for_valid_trackpoints)
from .ui_text import d
from .unit_conversions import (
    convert_m_to_km, convert_mps_to_kmph, minutes_from_start)


def render_map(path):
    """Draw path on map with leaflet.js.

    Parameters
    ----------
    path : dict
        A path that has at least the entries 'timestamps' and 'coords'.

    Returns
    -------
    html : str
        HTML representation of the rendered map.
    """
    m = make_map(path)
    return m.get_root().render()


def make_map(path):
    """Create folium map.

    Parameters
    ----------
    path : dict
        Path with entry 'coords': latitude and longitude coordinates in radians

    Returns
    -------
    m : folium.Map
        Map with path
    """
    coords = np.rad2deg(check_coords(path["coords"]))
    if len(coords) == 0:
        m = folium.Map()
    else:
        center = np.mean(coords, axis=0)
        distance_markers = generate_distance_markers(path)

        # TODO find a way to colorize path according to velocities
        # valid_velocities = np.isfinite(path["velocities"])
        # path["velocities"][np.logical_not(valid_velocities)] = 0.0

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
    return m


def generate_distance_markers(path):
    """Generate indices of distance markers.

    Parameters
    ----------
    path : dict
        A path that has at least the entries 'timestamps' and 'coords'.

    Returns
    -------
    marker_indices : dict
        Mapping of label (e.g., '1 km') to corresponding index of the path.
    """
    distances, _ = compute_distances_for_valid_trackpoints(path)
    total_distance = distances[-1]
    marker_dist = appropriate_partition(total_distance)
    thresholds = np.arange(marker_dist, int(total_distance), marker_dist)
    indices = np.searchsorted(distances, thresholds)
    marker_indices = {d.display_distance(threshold): index
                      for threshold, index in zip(thresholds, indices)}
    return marker_indices


def plot_velocity_histogram(path, ax):
    """Plot velocity histogram.

    Parameters
    ----------
    path : dict
        Path with entry 'velocities'

    ax : Matplotlib axis
        Axis on which we draw
    """
    velocities = path["velocities"]
    finite_velocities = np.isfinite(velocities)
    velocities = velocities[finite_velocities]
    if np.any(np.nonzero(velocities)):
        no_outlier = np.logical_not(is_outlier(velocities))
        velocities = convert_mps_to_kmph(velocities[no_outlier])
        delta_ts = np.gradient(
            path["timestamps"])[finite_velocities][no_outlier]

        ax.hist(velocities, bins=50, weights=delta_ts)
    ax.set_xlabel("Velocity [km/h]")
    ax.set_ylabel("Percentage")
    ax.set_yticks(())


def plot_elevation(path, ax, filter=True):
    """Plot elevation over distance.

    Parameters
    ----------
    path : dict
        Path with entries 'coords' and 'altitudes'

    ax : Matplotlib axis
        Axis on which we draw

    filter : bool, optional (default: True)
        Filter altitude data
    """
    distances_in_m, valid_trackpoints = \
        compute_distances_for_valid_trackpoints(path)
    if len(distances_in_m) > 0:
        distances_in_km = convert_m_to_km(distances_in_m)
        total_distance_in_m = np.nanmax(distances_in_m)

        altitudes = path["altitudes"][valid_trackpoints]
        # TODO exactly 0 seems to be an indicator for an error, a better
        # method would be to detect jumps
        valid_altitudes = np.logical_and(
            np.isfinite(altitudes), altitudes != 0.0)
        distances_in_km = distances_in_km[valid_altitudes]
        altitudes = altitudes[valid_altitudes]
        if len(altitudes) == 0:
            return

        if filter:
            altitudes = filter_median_average(
                altitudes, config["plot"]["filter_width"])

        gain, loss, slope_in_percent = elevation_summary(
            altitudes, total_distance_in_m)

        ax.set_title(f"Elevation gain: {int(np.round(gain, 0))} m, "
                     f"loss: {int(np.round(loss, 0))} m, "
                     f"slope {np.round(slope_in_percent, 2)}%")
        ax.fill_between(
            distances_in_km, np.zeros_like(altitudes), altitudes, alpha=0.3)
        ax.plot(distances_in_km, altitudes)
        ax.set_xlim((0, convert_m_to_km(total_distance_in_m)))
        ax.set_ylim((min(altitudes), 1.1 * max(altitudes)))
    ax.set_xlabel("Distance [km]")
    ax.set_ylabel("Elevation [m]")


def plot_speed_heartrate(vel_axis, hr_axis, path):
    """Plot velocities and heartrates over time.

    Parameters
    ----------
    vel_axis : Matplotlib axis
        Axis on which we draw velocities

    hr_axis : Matplotlib axis
        Axis on which we draw heartrate data

    path : dict
        Path with entries 'timestamps', 'velocities', and 'heartrates'

    Returns
    -------
    handles : list
        Line handles to create a legend

    labels : list
        Labels for lines to create a legend
    """
    time_in_min = minutes_from_start(path["timestamps"])
    velocities = convert_mps_to_kmph(
        filter_median_average(path["velocities"],
                              config["plot"]["filter_width"]))
    heartrates = filtered_heartrates(path, config["plot"]["filter_width"])

    matplotlib.rcParams["font.size"] = 10
    matplotlib.rcParams["legend.fontsize"] = 10

    handles = []
    labels = []

    if np.isfinite(velocities).any():
        vel_line, = vel_axis.plot(time_in_min, velocities, color="#4f86f7",
                                  alpha=0.8, lw=2)
        handles.append(vel_line)
        labels.append("Velocity")

        vel_axis.set_xlim((time_in_min[0], time_in_min[-1]))
        median_velocity = np.nanmedian(velocities)
        max_velocity = np.nanmax(velocities)
        vel_axis.set_ylim((0, max(2 * median_velocity, max_velocity)))
        vel_axis.set_xlabel("Time [min]")
        vel_axis.set_ylabel("Velocity [km/h]")
        vel_axis.tick_params(axis="both", which="both", length=0)
        vel_axis.grid(True)
    else:
        vel_axis.set_yticks(())

    if np.isfinite(heartrates).any():
        median_heartrate = np.nanmedian(heartrates)
        hr_line, = hr_axis.plot(time_in_min, heartrates, color="#a61f34",
                                alpha=0.8, lw=2)
        handles.append(hr_line)
        labels.append("Heart Rate")

        hr_axis.set_ylim((0, 2 * median_heartrate))
        hr_axis.set_ylabel("Heart Rate [bpm]")
        hr_axis.tick_params(axis="both", which="both", length=0)
        hr_axis.spines["top"].set_visible(False)
    else:
        hr_axis.set_yticks(())
    hr_axis.grid(False)

    return handles, labels
