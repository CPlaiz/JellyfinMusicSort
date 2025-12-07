import argparse
import json

from dotenv import load_dotenv

import spotify
from associate import get_jellyfin_for_spotify
from playback_entry import PlaybackEntry

parser = argparse.ArgumentParser(description="Download all songs from a user's Spotify playlists")
# Positional
parser.add_argument("history_dir", help="The directory that contains the Spotify json history files")

args = parser.parse_args()

history_dir = args.history_dir

load_dotenv()

with open("associated.json", "r") as f:
    association = json.load(f)

history = spotify.get_history(history_dir)

playback_entries = []

load_dotenv()
# get artist ids for track from jellyfin and use for PE

a = 0
b = 1

for item in history:
    spotify_track_uri = item["spotify_track_uri"]
    if not spotify_track_uri:
        continue
    spotify_track_id = spotify_track_uri.split(":")[2]
    jellyfin_track_id = get_jellyfin_for_spotify(association, spotify_track_id)
    if jellyfin_track_id is None:
        a  += 1
        print(f"{spotify_track_id} is not a jellyfin track ({item['master_metadata_album_artist_name']} - {item['master_metadata_track_name']})")
        continue
    else:
        b += 1

    duration = item["ms_played"]
    start_time = item["ts"]
    playback_entries.append(PlaybackEntry(spotify_track_id, None, start_time, duration))

print(a)
print(b)
