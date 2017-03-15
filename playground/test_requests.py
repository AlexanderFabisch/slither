import requests
import json


from slither.service import Service
self = Service()
activities = self._sync_files()
response = requests.get(
    "http://localhost:5000/api/sync",
    auth=("username", "mypassword"),
    json={"activities": activities})
print(response.text)
response = json.loads(response.text)
latest_on_client = response["latest_on_client"]
latest_on_server = response["latest_on_server"]

for data in self._get_sync_contents(latest_on_client):
    response = requests.post(
        "http://localhost:5000/api/activity",
        auth=("username", "mypassword"),
        json=data)
    print(response)

for filename in latest_on_server:
    response = requests.get(
        "http://localhost:5000/api/activity",
        auth=("username", "mypassword"),
        json={"filename": filename})
    print(response)
    print(response.text)