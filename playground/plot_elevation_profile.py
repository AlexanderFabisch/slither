import numpy as np
import sys
import matplotlib.pyplot as plt
from slither.tcx_loader import TcxLoader


filename = sys.argv[-1]
with open(filename, "r") as f:
    loader = TcxLoader(f.read())

a = loader.load()
path = a.get_path()
dts = np.diff(path["timestamps"])
distances_in_m = np.cumsum(dts * path["velocities"][:-1])
distances_in_km = distances_in_m / 1000.0
altitudes = path["altitudes"][:-1]

altitude_diffs = np.diff(altitudes)
up = sum(altitude_diffs[altitude_diffs > 0])
down = -sum(altitude_diffs[altitude_diffs < 0])
slope_in_percent = 100.0 * up / distances_in_m[-1]

fig = plt.figure(figsize=(5, 3), dpi=100)
ax = plt.subplot(111)
ax.set_title(f"{int(np.round(up, 0))} m up, {int(np.round(down, 0))} m down, "
             f"slope {np.round(slope_in_percent, 2)} %")
ax.fill_between(distances_in_km, np.zeros_like(altitudes), altitudes, alpha=0.3)
ax.plot(distances_in_km, altitudes)
ax.set_xlim((0, distances_in_km[-1]))
ax.set_ylim((min(altitudes), max(altitudes)))
ax.set_xlabel("Distance [km]")
ax.set_ylabel("Elevation [m]")
plt.tight_layout()
plt.show()
