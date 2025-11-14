import os
import time

import requests


class Jellyfin:
    def __init__(self, base_url, token_file=None):
        self.headers = {
            "X-Emby-Authorization": (
                'MediaBrowser Client="JellyfinPython", '
                'Device="PythonScript", '
                'DeviceId="12345", '
                'Version="10.10.7"'
            )
        }
        self.base_url = base_url
        self.session = requests.Session()
        self.token_file = token_file
        self.token = self.get_token_from_file()

    def save_token_to_file(self, token):
        with open(self.token_file, "w") as f:
            f.write(token)

    def get_token_from_file(self):
        if not self.token_file or not os.path.isfile(self.token_file):
            return None
        with open(self.token_file, "r") as f:
            return f.read().strip()

    def request_quickconnect_code(self):
        r = self.session.post(f"{self.base_url}/QuickConnect/Initiate", headers=self.headers)
        r.raise_for_status()
        data = r.json()
        print("📱 Your Quick Connect code:", data["Code"])
        print("👉 Go to your Jellyfin client or web app, open:")
        print("   Settings → Quick Connect → Enter the code above\n")
        return data["Secret"]

    def wait_for_authorization(self, secret):
        print("⏳ Waiting for Quick Connect authorization...")
        while True:
            r = self.session.get(f"{self.base_url}/QuickConnect/Connect", headers=self.headers, params={"secret": secret})
            if r.status_code == 200:
                data = r.json()
                if data.get("Authenticated"):
                    print("✅ Authenticated!")
                    return True
            elif r.status_code == 404:
                pass  # Not ready yet
            else:
                r.raise_for_status()
            time.sleep(3)

    def get_all_tracks(self, access_token):
        headers = {"X-MediaBrowser-Token": access_token}
        items = []
        start_index = 0
        limit = 100

        while True:
            params = {
                "IncludeItemTypes": "Audio",
                "Recursive": "true",
                "StartIndex": start_index,
                "Limit": limit,
                "SortBy": "Album,SortName",
                "SortOrder": "Ascending",
                "Fields": "ArtistItems,Album"
            }
            url = f"{self.base_url}/Items"
            r = self.session.get(url, headers=headers, params=params)
            r.raise_for_status()
            data = r.json()

            batch = data.get("Items", [])
            items.extend(batch)

            received_items = len(batch)
            print("Receiving items: " + str(start_index + received_items))

            if received_items < limit:
                break
            start_index += limit

        return items

    def authenticate(self, secret):
        headers = self.headers
        headers["Content-Type"] = "application/json"
        r = self.session.post(f"{self.base_url}/Users/AuthenticateWithQuickConnect", headers=headers,
                              json={"Secret": secret})
        data = r.json()
        return data.get("AccessToken")

    def request_token(self):
        secret = self.request_quickconnect_code()
        self.wait_for_authorization(secret)
        return self.authenticate(secret)

    def get_jellyfin_data(self):
        print("Fetching tracks...")
        tracks = self.get_all_tracks(self.token)
        print(f"Found {len(tracks)} tracks.\n")
