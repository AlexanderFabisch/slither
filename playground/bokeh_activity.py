# Demo with bokeh (https://docs.bokeh.org/en/latest/)
# Requirements: bokeh, pandas
# Start with:
# bokeh serve --show playground/bokeh_activity.py --args filename
import sys
import numpy as np
import pandas as pd
from slither.io.tcx_loader import TcxLoader
from slither.core.config import config
from slither.core.unit_conversions import convert_mps_to_kmph, minutes_from_start

from bokeh import plotting as plt
from bokeh.io import curdoc
from bokeh.layouts import column
from bokeh.models.sources import ColumnDataSource
from bokeh.models.tools import HoverTool
from bokeh.models import CustomJSHover


filename = sys.argv[-1]  # for example: "/home/afabisch/.slither/data/running_20190825_112213.tcx"
with open(filename, "r") as f:
    loader = TcxLoader(f.read())

activity = loader.load()
assert activity.has_path


path = activity.get_path()
path["latitudes"] = path["coords"][:, 0]
path["longitudes"] = path["coords"][:, 1]
del path["coords"]
df = pd.DataFrame(path)
df["timestamps"] = minutes_from_start(df["timestamps"])
time_in_min = df["timestamps"]
df["velocities"] = df["velocities"].rolling(config["plot"]["filter_width"]).median()
df["velocities"] = df["velocities"].rolling(config["plot"]["filter_width"]).mean()
df["velocities"] = convert_mps_to_kmph(df["velocities"])
df["heartrates"] = df["heartrates"].rolling(config["plot"]["filter_width"]).median()
df["zeros"] = np.zeros(len(df))
source = ColumnDataSource(df)

tooltips = [
    ("Time", "@timestamps{custom}"),
    ("Velocity", "@velocities km/h"),
    ("Heartrate", "@heartrates bpm"),
    ("Altitude", "@altitudes m"),
]
minutes_custom = CustomJSHover(code="""
    var minutes = Math.floor(special_vars.x)
    var seconds = Math.floor((special_vars.x - minutes) * 60.0)
    if (seconds < 10) {
        seconds = "0" + seconds
    }
    return minutes + ":" + seconds + " minutes"
""")
hover = HoverTool(
    tooltips=tooltips,
    formatters={"@timestamps": minutes_custom},
    mode="vline"
)
tools = [hover]

plot_velocity = plt.figure(
    title="Velocity",
    sizing_mode="stretch_width", plot_height=150,
    tools=tools,
    x_axis_label="Time [min]", y_axis_label="Velocity [km/h]")
plot_velocity.line(x="timestamps", y="velocities", color="blue", source=source)
plot_velocity.varea(x="timestamps", y1="zeros", y2="velocities", color="blue", fill_alpha=0.3, source=source)

plot_heartrate = plt.figure(
    title="Heartrate",
    sizing_mode="stretch_width", plot_height=150,
    tools=tools,
    x_axis_label="Time [min]", y_axis_label="Heartrate [bpm]")
plot_heartrate.line(x="timestamps", y="heartrates", color="red", source=source)
plot_heartrate.varea(x="timestamps", y1="zeros", y2="heartrates", color="red", fill_alpha=0.3, source=source)

plot_altitude = plt.figure(
    title="Heartrate",
    sizing_mode="stretch_width", plot_height=150,
    tools=tools,
    x_axis_label="Time [min]", y_axis_label="Altitude [m]")
plot_altitude.line(x="timestamps", y="altitudes", color="green", source=source)
plot_altitude.varea(x="timestamps", y1="zeros", y2="altitudes", color="green", fill_alpha=0.3, source=source)

layout = column(plot_velocity, plot_heartrate, plot_altitude)
curdoc().add_root(layout)
curdoc().title = filename
