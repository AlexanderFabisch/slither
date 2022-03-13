"""Data loaders."""
from slither.domain_model import Activity
from slither.io.fit_loader import read_fit
from slither.io.gpx_loader import read_gpx
from slither.io.polar_json_loader import read_polar_json
from slither.io.tcx_loader import read_tcx


class Loader:
    """Loader factory.

    Parameters
    ----------
    filename : str
        Name of the file that should be loaded.
    """
    def __init__(self, filename):
        self.filename = filename

    def get_loader(self, file_content=None):
        """Get loader.

        Parameters
        ----------
        file_content : str, optional (default: None)
            File content.

        Raises
        ------
        ValueError
            Cannot handle file format.
        """
        ending = self.filename.split(".")[-1]
        if ending.lower() == "gpx":
            return GpxLoader(file_content)
        if ending.lower() in ["tcx", "xml"]:
            return TcxLoader(file_content)
        if ending.lower() == "fit":
            return FitLoader(self.filename)
        raise ValueError("Cannot handle file format '%s'" % ending)


class FitLoader:
    """Loads Flexible and Interoperable Data Transfer (FIT) files.

    Parameters
    ----------
    filename : str
        Name of the file that should be loaded.
    """
    def __init__(self, filename):
        self.filename = filename

    def load(self):
        """Load file content.

        Returns
        -------
        activity : Activity
            Loaded activity.
        """
        metadata, path = read_fit(self.filename)
        activity = Activity(**metadata)
        if activity.has_path:
            activity.set_path(**path)
        return activity


class GpxLoader:
    """Loads GPS exchange format.

    Parameters
    ----------
    gpx_content : str
        Content of the file.
    """
    def __init__(self, gpx_content):
        self.content = gpx_content

    def load(self):
        """Load file content.

        Returns
        -------
        activity : Activity
            Loaded activity.
        """
        metadata, path = read_gpx(self.content)
        activity = Activity(**metadata)
        if activity.has_path:
            activity.set_path(**path)
        return activity


class PolarJsonLoader:
    """Loads JSON files from Polar data export.

    You can export your personal data from Polar flow at

        https://account.polar.com/#export

    Parameters
    ----------
    content : str
        Content of the file.
    """
    def __init__(self, content):
        self.content = content
        self.training = None
        self.metadata = None

    def load(self):
        """Load file content.

        Returns
        -------
        activity : Activity
            Loaded activity.
        """
        metadata, path = read_polar_json(self.content)
        activity = Activity(**metadata)
        if activity.has_path:
            activity.set_path(**path)
        return activity


class TcxLoader:
    """Loads training center XML (TCX).

    Parameters
    ----------
    content : str
        Content of the file.
    """
    def __init__(self, content):
        self.content = content

    def load(self):
        """Load file content.

        Returns
        -------
        activity : Activity
            Loaded activity.
        """
        metadata, path = read_tcx(self.content)
        activity = Activity(**metadata)
        if activity.has_path:
            activity.set_path(**path)
        return activity
