import os
from datetime import datetime, timezone
import json

def associate(spotify_data, jellyfin_data):
    association = {}
    spotify_tracks = spotify_data["tracks"]

    for i in range(len(spotify_tracks)):
        spotify_track = spotify_tracks[i]
        spotify_id = spotify_track["id"]
        spotify_name = spotify_track["name"]
        spotify_artists = [artist["name"] for artist in spotify_track["artists"]]
        spotify_album = spotify_track["album"]["name"]
        for jellyfin_track in jellyfin_data:
            jellyfin_id = jellyfin_track["Id"]
            jellyfin_name = jellyfin_track["Name"]
            jellyfin_album = jellyfin_track["Album"]
            artists_string = jellyfin_track["Artists"]
            jellyfin_artists = [artist.strip() for artist in artists_string] if len(artists_string) > 1 else [artist.strip() for artist in artists_string[0].split(",")]
            if spotify_name == jellyfin_name and spotify_artists == jellyfin_artists and spotify_album == jellyfin_album:
                if jellyfin_id in association:
                    association[jellyfin_id].append(spotify_id)
                else:
                    association[jellyfin_id] = [spotify_id]

    for jellyfin_track in jellyfin_data:
        jellyfin_id = jellyfin_track["Id"]
        jellyfin_name = jellyfin_track["Name"]
        artists_string = jellyfin_track["Artists"]
        jellyfin_artists = [artist.strip() for artist in artists_string] if len(artists_string) > 1 else [artist.strip() for artist in artists_string[0].split(",")]
        if not jellyfin_id in association:
            print(f"Could not associate '{jellyfin_artists} - {jellyfin_name}'")