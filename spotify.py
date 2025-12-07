import os
import time
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import json


class Spotify:
    def __init__(self, client_id, client_secret, redirect_uri, username=None, password=None):
        self.sp_client = spotipy.Spotify(
            auth_manager=SpotifyOAuth(
                client_id=client_id,
                client_secret=client_secret,
                redirect_uri=redirect_uri,
                scope="user-library-read playlist-read-private"
            )
        )

    def get_user_playlists_tracks(self):
        playlists = self.get_user_playlists()
        return get_tracks_from_user_playlists(playlists)

    def get_user_playlists(self):
        next_playlist_page = 0
        page_size = 25
        playlists = []
        print("Fetching playlists...")
        while True:
            playlists_response = self.sp_client.current_user_playlists(page_size, next_playlist_page * page_size)
            playlists += playlists_response["items"]
            if not playlists_response["next"]:
                break
            next_playlist_page += 1
        print("Fetched {} playlists".format(len(playlists)))
        playlist_tracks = {}
        print("Fetching playlist tracks...")
        for playlist in playlists:
            playlist_id = playlist["id"]
            playlist_name = playlist["name"]
            next_playlist_tracks_page = 0
            tracks = []
            while True:
                playlist_items_response = self.sp_client.playlist_tracks(
                    playlist_id=playlist_id,
                    limit=page_size,
                    offset=next_playlist_tracks_page * page_size
                )
                tracks += [item["track"] for item in playlist_items_response["items"]]
                if not playlist_items_response["next"]:
                    break
                next_playlist_tracks_page += 1
            playlist_tracks[playlist_id] = (playlist_name, tracks)
            print(f"Fetched {len(tracks)} tracks for '{playlist_name}'")
        print("Fetched tracks for {} playlists".format(len(playlists)))
        return playlist_tracks

    def get_spotify_data(self, track_ids):
        print(f"Getting data for {len(track_ids)} tracks")

        track_ids = [track_id for track_id in track_ids if track_id is not None]

        spotify_data = {"tracks": []}

        max_track_count = 50

        track_id_chunks = [track_ids[i:i + max_track_count] for i in range(0, len(track_ids), max_track_count)]

        for i, track_id_chunk in enumerate(track_id_chunks):
            print(f"Querying chunk {i + 1} of {len(track_id_chunks)} ({(i + 1) / len(track_id_chunks):.2f})")
            new_track_data = self.sp_client.tracks(track_id_chunk)
            spotify_data["tracks"].extend(new_track_data["tracks"])
            time.sleep(3)

        return spotify_data["tracks"]


def get_tracks_from_user_playlists(playlists):
    tracks_deduplicated = {}
    for (_, tracks) in playlists.values():
        for track in tracks:
            tracks_deduplicated[track["id"]] = track
    return list(tracks_deduplicated.values())

def get_history(history_dir):
    entries = []

    for file in os.listdir(history_dir):
        entries += json.load(open(history_dir + "/" + file))
    return entries

def extract_track_ids_from_history(items):
    track_ids = []
    for item in items:
        track_uri = item["spotify_track_uri"]
        if not track_uri:
            continue
        track_id = track_uri.split(":")[2]
        track_ids.append(track_id)
    return list(set(track_ids))
