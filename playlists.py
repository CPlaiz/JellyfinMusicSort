import argparse
import json
import os

from dotenv import load_dotenv

from jellyfin import Jellyfin
from spotify import Spotify


parser = argparse.ArgumentParser(description="Create Jellyfin playlists from spotify")
parser.add_argument("url", help="The URL to process")

parser.add_argument(
    "-pf", "--playlists-file",
    default="playlists.json",
    help="The file to store playlist template data (default: playlists.json)"
)

# optional
parser.add_argument(
    "-tf", "--token-file",
    nargs='?',
    help="The file to store the Jellyfin token"
)

args = parser.parse_args()

jellyfin_base_url = args.url
playlists_file = args.playlists_file
token_file = args.token_file


with open("associated.json", "r") as f:
    association = json.load(f)

load_dotenv()

jellyfin_playlist_templates = None
try:
    with open("playlists.json", "r") as f:
        jellyfin_playlist_templates = json.load(f)
except:
    pass

if not jellyfin_playlist_templates:
    jellyfin_playlist_templates = []
    spotify_client_id = os.getenv("SPOTIFY_CLIENT_ID")
    spotify_client_secret = os.getenv("SPOTIFY_CLIENT_SECRET")
    spotify_redirect_uri = os.getenv("SPOTIFY_REDIRECT_URI")

    spotify = Spotify(spotify_client_id, spotify_client_secret, spotify_redirect_uri)

    playlists = spotify.get_user_playlists()

    # TODO: kein associate sondern direct um lokale dateien zu berücksichtigen

    for id, data in playlists.items():
        name = data[0]
        items = data[1]
        playlist = []
        for item in items:
            for jellyfin_id, spotify_id in association.items():
                if spotify_id == item["id"]:
                    playlist.append(jellyfin_id)
                    break
        jellyfin_playlist_templates.append((name, playlist))

    with open("playlists.json", "w") as f:
        json.dump(jellyfin_playlist_templates, f)

jellyfin = Jellyfin(jellyfin_base_url, token_file)
jellyfin.load_or_request_token()

for name, tracks in jellyfin_playlist_templates:
    jellyfin.create_playlist(name, tracks)