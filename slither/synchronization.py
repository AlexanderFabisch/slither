"""Synchronization between data repository and client."""
import os
import json
import requests
from .io.utils import to_utf8


class Synchronizer:
    """Synchronize with remote data repository.

    Parameters
    ----------
    service : Service
        Slither service.

    remote : str
        URL to remote data repository.

    username : str
        Username for remote data repository.

    password : str
        Passwort for remote data repository.
    """
    def __init__(self, service, remote, username, password):
        self.service = service  # TODO minimize dependency on service
        self.remote = remote
        self.username = username
        self.password = password

    def sync_to_server(self):
        """Synchronize with server."""
        if self.remote is None:
            return

        activities = self._sync_files()
        response = requests.get(self.remote + "/api/sync",
                                auth=(self.username, self.password),
                                json={"activities": activities})
        if response.text == "Unauthorized Access":
            raise ValueError("Wrong username or password.")
        response = json.loads(response.text)

        for data in self._get_sync_contents(response["latest_on_client"]):
            requests.post(self.remote + "/api/activity",
                          auth=(self.username, self.password),
                          json=data)

        for filename in response["latest_on_server"]:
            response = requests.get(self.remote + "/api/activity",
                                    auth=(self.username, self.password),
                                    json={"filename": filename})
            data = json.loads(response.text)
            if data["content"] is None:
                self.service.registry.delete(
                    data["filename"], data["timestamp"])
            else:
                self.service.import_activity(
                    data["content"], data["filename"], data["timestamp"])

    def _sync_files(self):
        return self.service.registry.list()

    def _get_sync_contents(self, latest_on_client):
        data = []
        for filename in latest_on_client:
            full_filename = os.path.join(self.service.full_datadir, filename)
            if os.path.exists(full_filename):
                with open(full_filename, "r") as f:
                    content = to_utf8(f.read())
            else:
                content = None
            data.append({
                "content": content,
                "filename": filename,
                "timestamp": self.service.registry.timestamp(full_filename)})
        return data
