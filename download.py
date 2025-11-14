import argparse
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from spotdl import DownloaderOptionalOptions, Spotdl, Song
from spotdl.utils.search import get_simple_songs, songs_from_albums

SONG_DATA_CACHE_FILE = "song_data_cache.json"
DOWNLOAD_DIR = "download"

parser = argparse.ArgumentParser(description="Download all songs from a user's Spotify playlists")
parser.add_argument(
    "--no-fetch",
    default=False,
    help="Whether to not fetch playlist and song data from spotify (default: false)"
)
parser.add_argument(
    "--cookie-file",
    nargs="?",
    help="Path to the Youtube Music cookie file"
)

args = parser.parse_args()

no_fetch = args.no_fetch
cookie_file = args.cookie_file

load_dotenv()

downloader = Spotdl(
    client_id=os.getenv("SPOTIFY_CLIENT_ID"),
    client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
    user_auth=True,
    downloader_settings=DownloaderOptionalOptions(
        output=DOWNLOAD_DIR + "/{track-id}",
        format="opus",
        threads=10,
        filter_results=False,
        cookie_file=cookie_file
    )
)

downloaded_song_ids = [file.stem for file in Path(DOWNLOAD_DIR).iterdir() if file.is_file()]

try:
    with open(SONG_DATA_CACHE_FILE, "r") as f:
        songs_json = json.load(f)
        songs = [Song.from_dict(song_json) for song_json in songs_json]
except FileNotFoundError:
    songs = []

if not no_fetch or not songs:
    songs = get_simple_songs(["all-user-playlists"])
    print(f"Playlist songs: {len(songs)}")
    albums = set(song.album_id for song in songs if song.album_id is not None)
    print(f"Albums: {len(albums)}")
    songs.extend(songs_from_albums(list(albums)))

    dupe_filter = {}
    for song in songs:
        dupe_filter[song.url] = song

    songs = list(dupe_filter.values())

    with open(SONG_DATA_CACHE_FILE, "w") as f:
        json.dump([song.json for song in songs], f)

print(f"Total songs: {len(songs)}")

songs_to_download = [song for song in songs if song.song_id not in downloaded_song_ids]

print([song.name for song in songs_to_download])

print(f"Songs up for download: {len(songs_to_download)}")

downloader.download_songs(songs_to_download)
