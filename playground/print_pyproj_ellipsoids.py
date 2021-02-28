import pyproj
import rich


ellps_map = pyproj.get_ellps_map()
rich.print(ellps_map)
