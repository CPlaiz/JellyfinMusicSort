import os
from datetime import datetime, timezone
import json

stats_json_dir = "stats_json"

items = []

for file in os.listdir(stats_json_dir):
    items += json.load(open(stats_json_dir + "/" + file))

spotify_playback_entries = []

for item in items:
    track_uri = item["spotify_track_uri"]
    if not track_uri:
        continue
    track_id = track_uri.split(":")[2]
    timestamp = datetime.strptime(item["ts"], "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=timezone.utc).timestamp()
    time_played = item["ms_played"]
    spotify_playback_entries.append((track_id, timestamp, time_played))