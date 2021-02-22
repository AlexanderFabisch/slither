import numpy as np
from rich.table import Table
from rich.console import Console
from slither.service import Service
from slither.ui_text import d
from slither import domain_model
from sqlalchemy import func


s = Service()

# TODO filter invalid
records = s.database.session.query(domain_model.Record, func.rank().over(
    order_by=domain_model.Record.time.asc(),
    partition_by=(domain_model.Record.sport, domain_model.Record.distance)
).label("rank")).all()

table = Table(title="Records")
table.add_column("Sport")
table.add_column("Distance", justify="right")
table.add_column("Rank", justify="right")
table.add_column("Time", justify="right")
for record, rank in records:  # print date
    if rank >= 20 or not record.valid or np.isinf(record.time):
        continue
    table.add_row(
        d.display_sport(record.sport),
        d.display_distance(record.distance),
        str(rank),
        d.display_time(record.time))

console = Console()
console.print(table)
