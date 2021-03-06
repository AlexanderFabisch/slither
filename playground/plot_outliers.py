import sys
import numpy as np
import matplotlib.pyplot as plt
from slither.io.tcx_loader import TcxLoader
from slither.core.analysis import is_outlier
from slither.core.ui_text import convert_mps_to_kmph, minutes_from_start
from slither.core.visualization import filter_median_average
try:
    import seaborn as sns
    sns.set()
except ImportError:
    print("Seaborn not available, using default matplotlib style.")


filename = sys.argv[-1]
with open(filename, "r") as f:
    loader = TcxLoader(f.read())

a = loader.load()
path = a.get_path()

velocities = convert_mps_to_kmph(path["velocities"])
outliers = is_outlier(velocities, 5)
valid_velocities = velocities.copy()
valid_velocities[outliers] = np.nan
invalid_velocities = velocities.copy()
invalid_velocities[np.logical_not(outliers)] = np.nan

filtered_velocities = convert_mps_to_kmph(filter_median_average(path, 31))

minutes = minutes_from_start(path["timestamps"])

fig = plt.figure(figsize=(10, 3.5), dpi=100)
ax = plt.subplot(111)
ax.plot(minutes, valid_velocities)
ax.plot(minutes, invalid_velocities)
ax.plot(minutes, filtered_velocities)
ax.set_xlim((0, minutes[-1]))
ax.set_ylim((0, 1.2 * np.nanmax(valid_velocities)))
ax.set_xlabel("Time [min]")
ax.set_ylabel("Velocity [km/h]")
plt.tight_layout()
plt.show()
