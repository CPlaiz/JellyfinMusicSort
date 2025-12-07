import argparse
import os
from datetime import datetime, timezone
import json

def associate(spotify_data, jellyfin_data):
    association = []
    for i in range(len(spotify_data)):
        spotify_track = spotify_data[i]
        try:
            spotify_id = spotify_track["id"]
        except:
            print(spotify_track)
            raise Exception()
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
                association.append((jellyfin_id, spotify_id))

    """for jellyfin_track in jellyfin_data:
        jellyfin_id = jellyfin_track["Id"]
        jellyfin_name = jellyfin_track["Name"]
        artists_string = jellyfin_track["Artists"]
        jellyfin_artists = [artist.strip() for artist in artists_string] if len(artists_string) > 1 else [artist.strip() for artist in artists_string[0].split(",")]
        if not jellyfin_id in association:
            print(f"Could not associate '{jellyfin_artists} - {jellyfin_name}'")"""
    return association

def get_jellyfin_for_spotify(association, spotify_id):
    for associated_jellyfin_id, associated_spotify_id in association:
        if spotify_id == associated_spotify_id:
            return associated_jellyfin_id
    return None

def get_spotify_for_jellyfin(association, jellyfin_id):
    for associated_jellyfin_id, associated_spotify_id in association:
        if jellyfin_id == associated_jellyfin_id:
            return associated_jellyfin_id
    return None