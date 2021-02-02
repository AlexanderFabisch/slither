import os
import matplotlib.pyplot as plt
from slither.gui.activity import plot
from slither.tcx_loader import TcxLoader


fig = plt.figure(figsize=(5, 3), dpi=100)
fig.subplots_adjust(left=0.11, right=0.88, bottom=0.15, top=0.98)
ax = plt.subplot(111)
twin_ax = ax.twinx()

with open(os.path.join("test_data", "running.tcx"), "r") as f:
    loader = TcxLoader(f.read())

a = loader.load()
lines, labels = plot(ax, twin_ax, a.get_path())
fig.legend(handles=lines, labels=labels, loc="upper center")

plt.show()
