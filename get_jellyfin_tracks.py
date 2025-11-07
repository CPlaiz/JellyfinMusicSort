import json

import requests
import time

JELLYFIN_URL = "https://jellyfin.cplaiz.dev"
HEADERS = {
    "X-Emby-Authorization": (
        'MediaBrowser Client="JellyfinPython", '
        'Device="PythonScript", '
        'DeviceId="12345", '
        'Version="1.0"'
    )
}

session = requests.Session()


def request_quickconnect_code():
    r = session.post(f"{JELLYFIN_URL}/QuickConnect/Initiate", headers=HEADERS)
    r.raise_for_status()
    data = r.json()
    print("📱 Your Quick Connect code:", data["Code"])
    print("👉 Go to your Jellyfin client or web app, open:")
    print("   Settings → Quick Connect → Enter the code above\n")
    return data["Secret"]


def wait_for_authorization(secret):
    print("⏳ Waiting for Quick Connect authorization...")
    print(secret)
    while True:
        r = session.get(f"{JELLYFIN_URL}/QuickConnect/Connect", headers=HEADERS, params={"secret": secret})
        if r.status_code == 200:
            data = r.json()
            if data.get("Authenticated"):
                print("✅ Authorized!")
                return True
        elif r.status_code == 404:
            pass  # Not ready yet
        else:
            r.raise_for_status()
        time.sleep(3)


def get_all_tracks(access_token):
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
        url = f"{JELLYFIN_URL}/Items"
        r = session.get(url, headers=headers, params=params)
        r.raise_for_status()
        data = r.json()

        batch = data.get("Items", [])
        items.extend(batch)

        if len(batch) < limit:
            break
        start_index += limit
        break

    return items


def authenticate(secret):
    r = session.get(f"{JELLYFIN_URL}/Users/AuthenticateWithQuickConnect", headers=HEADERS, json={"Secret": secret})
    print(r.status_code)
    data = r.json()
    return data.get("AccessToken")


if __name__ == "__main__":
    secret = request_quickconnect_code()
    wait_for_authorization(secret)

    access_token = authenticate(secret)

    print("\n🎶 Fetching your tracks...")
    tracks = get_all_tracks(access_token)
    print(f"🎵 Found {len(tracks)} tracks.\n")

    with open("jellyfin_data.json", "w") as f:
        json.dump(tracks, f)
