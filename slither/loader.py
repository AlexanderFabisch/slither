from slither.domain_model import Activity
from slither.io.fit_loader import read_fit
from slither.io.gpx_loader import read_gpx
from slither.io.polar_json_loader import read_polar_json
from slither.io.tcx_loader import read_tcx


class Loader:
    def __init__(self, filename):
        self.filename = filename

    def get_loader(self, file_content=None):
        ending = self.filename.split(".")[-1]
        if ending.lower() == "gpx":
            return GpxLoader(file_content)
        if ending.lower() in ["tcx", "xml"]:
            return TcxLoader(file_content)
        if ending.lower() == "fit":
            return FitLoader(self.filename)
        else:
            raise ValueError("Cannot handle file format '%s'" % ending)


class FitLoader:
    """Loads Flexible and Interoperable Data Transfer (FIT) files."""
    def __init__(self, filename):
        self.filename = filename

    def load(self):
        metadata, path = read_fit(self.filename)
        activity = Activity(**metadata)
        if activity.has_path:
            activity.set_path(**path)
        return activity


class GpxLoader:
    """Loads GPS exchange format."""
    def __init__(self, gpx_content):
        self.content = gpx_content

    def load(self):
        metadata, path = read_gpx(self.content)
        activity = Activity(**metadata)
        if activity.has_path:
            activity.set_path(**path)
        return activity


class PolarJsonLoader:
    """Loads JSON files from Polar data export.

    You can export your personal data from Polar flow at

        https://account.polar.com/#export
    """
    def __init__(self, content):
        self.content = content
        self.training = None
        self.metadata = None

    def load(self):
        metadata, path = read_polar_json(self.content)
        activity = Activity(**metadata)
        if activity.has_path:
            activity.set_path(**path)
        return activity


class TcxLoader:
    """Loads training center XML (TCX)."""
    def __init__(self, content):
        self.content = content

    def load(self):
        metadata, path = read_tcx(self.content)
        activity = Activity(**metadata)
        if activity.has_path:
            activity.set_path(**path)
        return activity
