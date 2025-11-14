import os
import time
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import json


class Spotify:
    def __init__(self, client_id, client_secret, redirect_uri, history_dir):
        self.sp_client = spotipy.Spotify(
            auth_manager=SpotifyOAuth(
                client_id=client_id,
                client_secret=client_secret,
                redirect_uri=redirect_uri,
                scope="user-library-read"
            )
        )
        self.history_dir = history_dir


    def extract_track_ids_from_history(self):
        items = []

        for file in os.listdir(self.history_dir):
            items += json.load(open(self.history_dir + "/" + file))

        track_ids = []

        for item in items:
            track_uri = item["spotify_track_uri"]
            if not track_uri:
                continue
            track_id = track_uri.split(":")[2]
            track_ids.append(track_id)
        return list(set(track_ids))

    def get_spotify_data(self, track_ids):
        print(f"Getting data for {len(track_ids)} tracks")

        spotify_data = {"tracks": []}

        max_track_count = 50

        track_id_chunks = [track_ids[i:i + max_track_count] for i in range(0, len(track_ids), max_track_count)]

        for i, track_id_chunk in enumerate(track_id_chunks):
            print(f"Querying chunk {i + 1} of {len(track_id_chunks)} ({(i + 1) / len(track_id_chunks):.2f})")
            new_track_data = self.sp_client.tracks(track_id_chunk)
            spotify_data["tracks"].extend(new_track_data["tracks"])
            time.sleep(3)

        return spotify_data
