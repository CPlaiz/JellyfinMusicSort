import os
import time
from datetime import datetime, timezone
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import json

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope="user-library-read"))

stats_json_dir = "stats_json"

items = []

for file in os.listdir(stats_json_dir):
    items += json.load(open(stats_json_dir + "/" + file))

track_ids = []

for item in items:
    track_uri = item["spotify_track_uri"]
    if not track_uri:
        continue
    track_id = track_uri.split(":")[2]
    track_ids.append(track_id)

track_ids = list(set(track_ids))

print(f"Found {len(track_ids)} tracks")

spotify_data = []

max_track_count = 50

track_id_chunks = [track_ids[i:i + 50] for i in range(0, len(track_ids), 50)]
for track_id_chunk in track_id_chunks:
    spotify_data += sp.tracks(track_ids[0:10])
    time.sleep(3)

with open("spotify_data.json", "w") as outfile:
    json.dump(spotify_data, outfile)
    print(f"Wrote {len(spotify_data)} tracks to spotify_data.json")
