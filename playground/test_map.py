from slither.core.visualization import render_map
from slither.service import Service


s = Service()
activities = s.list_activities()
a = [a for a in activities if a.has_path][0]
print(a.start_time)

map = render_map(a)
with open("map.html", "w") as f:
    f.write(map)