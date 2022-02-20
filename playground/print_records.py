import sys
from rich.table import Table
from rich.console import Console
from slither.loader import TcxLoader
from slither.core.analysis import fastest_part, interpolate_nan
from slither.core.ui_text import d


filename = sys.argv[-1]
with open(filename, "r") as f:
    loader = TcxLoader(f.read())

a = loader.load()
assert a.has_path
path = a.get_path()

distances = [100, 200, 400, 800, 1000, 1500, 1600, 2000, 3000, 5000, 10000, 21097.5, 41195]

table = Table(title="Records")
table.add_column("Distance", justify="right")
table.add_column("Time", justify="right")
for distance in distances:
    velocities = interpolate_nan(path["velocities"])
    record = fastest_part(a.sport, path["timestamps"], velocities, distance)
    table.add_row(d.display_distance(distance), d.display_time(record))
console = Console()
console.print(table)
