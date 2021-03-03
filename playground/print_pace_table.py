import sys
from rich.table import Table
from rich.console import Console
from slither.io.tcx_loader import TcxLoader
from slither.analysis import get_paces
from slither.ui_text import d


filename = sys.argv[-1]
with open(filename, "r") as f:
    loader = TcxLoader(f.read())

a = loader.load()
pace_table = get_paces(a.get_path(), a.sport)

table = Table(title="Paces")
table.add_column("Distance", justify="right")
table.add_column("Pace (Time per km)", justify="right")
for distance, pace in pace_table:
    table.add_row(d.display_distance(distance), d.display_time(pace))
console = Console()
console.print(table)
