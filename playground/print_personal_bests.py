from rich.table import Table
from rich.console import Console
from rich import box
from slither.service import Service
from slither.ui_text import d
from slither import domain_model
from sqlalchemy import func


s = Service()

subquery = s.database.session.query(domain_model.Record, func.rank().over(
    order_by=domain_model.Record.time.asc(),
    partition_by=(domain_model.Record.sport, domain_model.Record.distance)
).label("rank")).subquery()
query = s.database.session.query(
    subquery).filter(subquery.c.rank <= 30).filter(
    subquery.c.valid).filter(subquery.c.time != float("inf"))

table = Table(title="Records", box=box.MINIMAL_HEAVY_HEAD)
table.add_column("Sport")
table.add_column("Distance", justify="right")
table.add_column("Rank", justify="right")
table.add_column("Time", justify="right")
table.add_column("Date")
table.add_column("Activity distance")
table.add_column("Activity time")
for _, sport, distance, time, valid, activity_id, rank in query.all():  # print date
    assert valid
    activity = s.database.session.query(
        domain_model.Activity).filter(
        domain_model.Activity.id == activity_id).first()
    table.add_row(
        d.display_sport(sport),
        d.display_distance(distance),
        str(rank),
        d.display_time(time),
        d.display_date(activity.start_time),
        d.display_distance(activity.distance),
        d.display_time(activity.time))

console = Console()
console.print(table)
