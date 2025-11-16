import argparse
import os
from dotenv import load_dotenv

from downloader import Downloader

parser = argparse.ArgumentParser(description="Download all songs from a user's Spotify playlists")
# Positional
parser.add_argument("directory", help="Path to the directory to save Audio files to")

# Flags
parser.add_argument(
    "--no-fetch",
    action="store_false",
    help="Don't fetch playlist and song data from spotify"
)
parser.add_argument(
    "--extend-albums",
    action="store_true",
    help="Include all songs' albums"
)
parser.add_argument(
    "--cache-file",
    default="song_data_cache.json",
    help="The file for saving spotify cache data (default: song_data_cache.json)"
)
parser.add_argument(
    "--cookie-file",
    nargs="?",
    help="Path to the Youtube Music cookie file"
)

args = parser.parse_args()

load_dotenv()

downloader = Downloader(
    spotify_client_id=os.getenv("SPOTIFY_CLIENT_ID"),
    spotify_client_secret=os.getenv("SPOTIFY_CLIENT_SECRET"),
    download_dir=args.directory,
    cookie_file=args.cookie_file,
    threads=10,
    cache_file=args.cache_file
)
fetch = not args.no_fetch

songs = downloader.fetch_song_data(args.extend_albums) if fetch else downloader.load_song_cache()
downloader.download(songs)