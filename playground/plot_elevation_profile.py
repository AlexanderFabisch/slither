import numpy as np
import sys
import matplotlib.pyplot as plt
from slither.tcx_loader import TcxLoader
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

fig = plt.figure(figsize=(5, 3), dpi=100)
ax = plt.subplot(111)
ax.set_title(f"{int(np.round(up, 0))} m up, {int(np.round(down, 0))} m down, "
             f"slope {np.round(slope_in_percent, 2)} %")
ax.fill_between(distances_in_km, np.zeros_like(altitudes), altitudes, alpha=0.3)
ax.plot(distances_in_km, altitudes)
ax.set_xlim((0, total_distance_in_km))
ax.set_ylim((min(altitudes), 1.1 * max(altitudes)))
ax.set_xlabel("Distance [km]")
ax.set_ylabel("Elevation [m]")
plt.tight_layout()
plt.show()
