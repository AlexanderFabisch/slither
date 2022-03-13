"""Local registry of activity files."""
import os
import json
import time
from .io.utils import to_utf8


class Registry:
    """Local registry of activity files.

    Parameters
    ----------
    temp_dir : str
        Directory to store the activity files
    """
    def __init__(self, temp_dir):
        self.temp_dir = temp_dir
        self.registry_filename = os.path.join(temp_dir, "registry.json")

        self._make_base_path()
        if os.path.exists(self.registry_filename):
            with open(self.registry_filename, "r") as f:
                self.registry = json.load(f)
        else:
            self.registry = {}

    def _make_base_path(self):
        """Create base path directory."""
        base_path = self._base_path()
        if not os.path.exists(base_path):
            os.makedirs(base_path)

    def update(self, content, filename, timestamp=None):
        """Add activity to registry.

        Parameters
        ----------
        content : str or None
            Content of activity file.

        filename : str
            Name of activity file.

        timestamp : float, optional (default: None)
            Timestamp at which the activity has been stored.
        """
        filename = self._filename(filename)
        if timestamp is None:
            timestamp = time.time()

        if content is None:
            if os.path.exists(filename):
                os.remove(filename)
        else:
            with open(filename, "wb") as f:
                f.write(to_utf8(content))
        self.registry[filename] = timestamp
        self._write()

    def _filename(self, filename):
        """Full filename.

        Parameters
        ----------
        filename : str
            Name of activity file without path.

        Returns
        -------
        filename : str
            Full path of activity file.
        """
        base_path = self._base_path()
        while base_path in filename:
            filename = filename.replace(base_path, "")
        filename = os.path.join(base_path, filename)
        return filename

    def _write(self):
        """Write registry."""
        with open(self.registry_filename, "w") as f:
            json.dump(self.registry, f)

    def delete(self, filename, timestamp=None):
        """Delete activity from registry.

        Parameters
        ----------
        filename : str
            Name of activity file.

        timestamp : float, optional (default: None)
            Timestamp at which the activity has been stored.
        """
        self.update(None, filename, timestamp)

    def list(self):
        """List activities.

        Returns
        -------
        activities : dict
            List of activities. Maps filenames to timestamps.
        """
        base_path = self._base_path()
        return dict((k.replace(base_path, ""), v)
                    for k, v in self.registry.items())

    def timestamp(self, filename):
        """Get timestamp of an ativity file.

        Parameters
        ----------
        filename : str
            Name of activity file.

        Returns
        -------
        timestamp : float
            Timestamp at which the activity has been stored.
        """
        filename = self._filename(filename)
        return self.registry[filename]

    def content(self, filename):
        """Get content of an activity file.

        Parameters
        ----------
        filename : str
            Name of activity file.

        Returns
        -------
        content : str or None
            Content of activity file.
        """
        filename = self._filename(filename)
        if os.path.exists(filename):
            with open(filename) as f:
                return f.read()
        else:
            return None

    def _base_path(self):
        """Base path.

        Returns
        -------
        base_path : str
            Path at which activity files will be stored.
        """
        return os.path.join(self.temp_dir, "data") + os.sep
