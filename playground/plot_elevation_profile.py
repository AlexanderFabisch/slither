import sys
import matplotlib.pyplot as plt
from slither.loader import TcxLoader
from slither.core.visualization import plot_elevation
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
fig = plt.figure(figsize=(5, 3), dpi=100)
ax = plt.subplot(111)
plot_elevation(path, ax)
plot_elevation(path, ax, filter=False)
plt.tight_layout()
plt.show()
