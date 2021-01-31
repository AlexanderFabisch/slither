from .tcx_loader import TcxLoader
from .gpx_loader import GpxLoader
from .polar_json_loader import PolarJsonLoader


class Loader:
    def __init__(self, filename):
        self.filename = filename

    def get_loader(self, file_content, **kwargs):
        ending = self.filename.split(".")[-1]
        if ending.lower() == "gpx":
            return GpxLoader(file_content)
        if ending.lower() in ["tcx", "xml"]:
            return TcxLoader(file_content)
        if ending.lower() == "json":
            return PolarJsonLoader(file_content, **kwargs)
        else:
            raise ValueError("Cannot handle file format '%s'" % ending)
