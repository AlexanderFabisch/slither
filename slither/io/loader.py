from slither.io.tcx_loader import TcxLoader
from slither.io.gpx_loader import GpxLoader


class Loader:
    def __init__(self, filename):
        self.filename = filename

    def get_loader(self, file_content):
        ending = self.filename.split(".")[-1]
        if ending.lower() == "gpx":
            return GpxLoader(file_content)
        if ending.lower() in ["tcx", "xml"]:
            return TcxLoader(file_content)
        else:
            raise ValueError("Cannot handle file format '%s'" % ending)
