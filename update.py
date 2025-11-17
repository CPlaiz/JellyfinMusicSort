import argparse
import json
import os

from dotenv import load_dotenv

from associate import associate
from jellyfin import Jellyfin
from spotify import Spotify

load_dotenv()

parser = argparse.ArgumentParser(description="Process a URL input")
parser.add_argument("url", help="The URL to process")

parser.add_argument(
    "-jd", "--jellyfin-data-file",
    default="jellyfin_data.json",
    help="The file to store jellyfin track data (default: jellyfin_data.json)"
)

parser.add_argument(
    "-sd", "--spotify-data-file",
    default="spotify_data.json",
    help="The file to store spotify track data (default: spotify_data.json)"
)

parser.add_argument(
    "-e", "--excluded",
    default="",
    help="The excluded update sources (default: '', possible values: spotify,jellyfin)"
)

# optional
parser.add_argument(
    "-tf", "--token-file",
    nargs='?',
    help="The file to store the Jellyfin token"
)
parser.add_argument(
    "-hd", "--history-dir",
    nargs='?',
    default="history",
    help="The directory that contains the Spotify json history files (default: history)"
)

args = parser.parse_args()

jellyfin_base_url = args.url
jellyfin_data_file = args.jellyfin_data_file
spotify_data_file = args.spotify_data_file
history_dir = args.history_dir
token_file = args.token_file
excluded = args.excluded.split(',')

spotify_client_id = os.getenv("SPOTIFY_CLIENT_ID")
spotify_client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
spotify_redirect_uri = os.getenv("SPOTIFY_REDIRECT_URI")

jellyfin = Jellyfin(jellyfin_base_url, token_file)
spotify = Spotify(spotify_client_id, spotify_client_secret, spotify_redirect_uri)

jellyfin_data = None
if "jellyfin" in excluded:
    try:
        with open(jellyfin_data_file, "r") as f:
            jellyfin_data = json.load(f)
    except:
        pass

if not jellyfin_data:
    jellyfin_data = jellyfin.get_jellyfin_data()
    with open(jellyfin_data_file, "w") as f:
        json.dump(jellyfin_data, f)

spotify_data = None
if "spotify" in excluded:
    try:
        with open(spotify_data_file, "r") as f:
            spotify_data = json.load(f)
    except:
        pass

if not spotify_data:
    if history_dir:
        track_ids = spotify.extract_track_ids_from_history(history_dir)
    else:
        track_ids = spotify.get_user_playlist_track_ids()
    spotify_data = spotify.get_spotify_data(track_ids)
    with open(spotify_data_file, "w") as f:
        json.dump(spotify_data, f)

associated = associate(spotify_data, jellyfin_data)
with open("associated.json", "w") as f:
    json.dump(associated, f)