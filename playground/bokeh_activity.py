# Demo with bokeh (https://docs.bokeh.org/en/latest/)
# Start with:
# bokeh serve --show playground/bokeh_activity.py
import numpy as np
from slither.io.tcx_loader import TcxLoader
from slither.core.config import config
from slither.core.analysis import filtered_heartrates, filter_median_average
from slither.core.unit_conversions import convert_mps_to_kmph, minutes_from_start

from bokeh import plotting as plt
from bokeh.io import curdoc
from bokeh.layouts import column, row


filename = "/home/afabisch/.slither/data/running_20190825_112213.tcx"  # TODO
with open(filename, "r") as f:
    loader = TcxLoader(f.read())

activity = loader.load()
assert activity.has_path


path = activity.get_path()
time_in_min = minutes_from_start(path["timestamps"])
velocities = convert_mps_to_kmph(
    filter_median_average(path["velocities"], config["plot"]["filter_width"]))

heartrates = filtered_heartrates(path, config["plot"]["filter_width"])

tools = "wheel_zoom,xbox_select,reset"

plot_velocity = plt.figure(
    title="Velocity",
    sizing_mode="stretch_width", plot_height=150,
    tools=tools,
    x_axis_label="Time [min]", y_axis_label="Velocity [km/h]")
plot_velocity.varea(x=time_in_min, y1=np.zeros_like(velocities), y2=velocities, color="blue", fill_alpha=0.3)

plot_heartrate = plt.figure(
    title="Heartrate",
    sizing_mode="stretch_width", plot_height=150,
    tools=tools,
    x_axis_label="Time [min]", y_axis_label="Heartrate [bpm]")
plot_heartrate.varea(x=time_in_min, y1=np.zeros_like(heartrates), y2=heartrates, color="red", fill_alpha=0.3)

layout = column(plot_velocity, plot_heartrate)
curdoc().add_root(layout)
curdoc().title = filename
