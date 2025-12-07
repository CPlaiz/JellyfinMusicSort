import argparse
import json
import os

from dotenv import load_dotenv

from associate import associate
from jellyfin import Jellyfin
from spotify import Spotify, extract_track_ids_from_history, get_history

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
    help="The excluded update sources (default: '', possible values: spotify,jellyfin,association)"
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
    help="The directory that contains the Spotify json history files"
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

jellyfin.load_or_request_token()

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
    spotify_data = spotify.get_user_playlists_tracks()
    if history_dir:
        history = get_history(history_dir)
        history_track_ids = extract_track_ids_from_history(history)
        print(len(history_track_ids))
        track_ids = [track["id"] for track in spotify_data]
        track_ids = [track_id for track_id in track_ids if track_id not in history_track_ids]
        print(len(track_ids))
        spotify_data.extend(spotify.get_spotify_data(track_ids))

    with open(spotify_data_file, "w") as f:
        json.dump(spotify_data, f)

associated = None
if "association" in excluded:
    try:
        with open("associated.json", "r") as f:
            associated = json.load(f)
    except:
        pass

if not associated:
    associated = associate(spotify_data, jellyfin_data)
    with open("associated.json", "w") as f:
        json.dump(associated, f)
