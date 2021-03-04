from rich.table import Table
from rich.console import Console
from slither.service import Service
from slither.core.ui_text import d


s = Service()
summaries = s.summarize_years()
table = Table(title="Activities per Year")
table.add_column("Start")
table.add_column("End")
table.add_column("Activities", justify="right")
table.add_column("Time", justify="right")
table.add_column("Distance", justify="right")
for summary in summaries:
    table.add_row(
        d.display_date(summary["start"]), d.display_date(summary["end"]),
        str(summary["n_activities"]), d.display_time(summary["time"]),
        d.display_distance(summary["distance"]))
console = Console()
console.print(table)
