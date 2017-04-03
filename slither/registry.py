import os
import json
import time
from .data_utils import to_utf8


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
        base_path = self._base_path()
        if not os.path.exists(base_path):
            os.makedirs(base_path)

    def update(self, content, filename, timestamp=None):
        filename = self._filename(filename)
        if timestamp is None:
            timestamp = time.time()

        if content is None:
            if os.path.exists(filename):
                os.remove(filename)
        else:
            with open(filename, "w") as f:
                f.write(str(to_utf8(content)))
        self.registry[filename] = timestamp
        self._write()

    def _filename(self, filename):
        base_path = self._base_path()
        while base_path in filename:
            filename = filename.replace(base_path, "")
        filename = os.path.join(base_path, filename)
        return filename

    def _write(self):
        with open(self.registry_filename, "w") as f:
            json.dump(self.registry, f)

    def delete(self, filename, timestamp=None):
        self.update(None, filename, timestamp)

    def list(self):
        base_path = self._base_path()
        return dict((k.replace(base_path, ""), v)
                    for k, v in self.registry.items())

    def timestamp(self, filename):
        filename = self._filename(filename)
        return self.registry[filename]

    def content(self, filename):
        filename = self._filename(filename)
        if os.path.exists(filename):
            with open(filename) as f:
                return f.read()
        else:
            return None

    def _base_path(self):
        return os.path.join(self.temp_dir, "data") + os.sep
