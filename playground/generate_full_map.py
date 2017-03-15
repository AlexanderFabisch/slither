import jinja2
import numpy as np
from slither.service import Service
from slither.domain_model import Trackpoint
from slither.data_utils import check_coords


TEMPLATE = """<!DOCTYPE html>
<html>
<head>
    <meta charset='utf-8' />
    <title></title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.0.2/dist/leaflet.css" />
    <script src="https://unpkg.com/leaflet@1.0.2/dist/leaflet.js"></script>
    <style>
        #mapdiv {
            width: 100%;
            height: 100%;
            position: absolute;
            top: 0;
            left: 0;

            transition: height 0.5s ease-in-out;
        }
    </style>
</head>
<body>

<div id="mapdiv"></div>
<!-- Map rendered with Leaflet http://leafletjs.com/ and OpenStreetMap -->
<script>
var map = L.map('mapdiv');
L.tileLayer('http://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 18
}).addTo(map);
{% for path in coords %}
var latlngs = [
{% for lat, lon in path %}
    [{{ lat }}, {{ lon }}],
{% endfor %}
];
var path = L.polyline(latlngs, {color: 'blue'}).addTo(map);
{% endfor %}
map.fitBounds(path.getBounds());

$mapdiv.on('map-container-resize', function () {
   setTimeout(function(){ map.invalidateSize()}, 400);
});
</script>

</body>
</html>
"""


def all_trackpoints():
    s = Service()
    trackpoints = s.database.session.query(Trackpoint).all()
    timestamps = np.array([t.timestamp for t in trackpoints])

    coords = np.array([(t.latitude, t.longitude) for t in trackpoints],
                      dtype=np.float)
    split_indices = np.where(np.abs(np.diff(timestamps)) > 100.0)[0]
    coords = np.array_split(coords, split_indices + 1)

    new_coords = []
    for path in coords:
        new_coords.append(np.rad2deg(check_coords(path)))
    return new_coords


def render_map(coords):
    template = jinja2.Template(TEMPLATE)
    return template.render(coords=coords)


# http://leafletjs.com
coords = all_trackpoints()
html = render_map(coords)
with open("index.html", "w") as f:
    f.write(html)
