import json
import os
from pathlib import Path

from spotdl import DownloaderOptionalOptions, Spotdl, Song
from spotdl.utils.search import get_simple_songs, songs_from_albums


class Downloader:
    def __init__(self, spotify_client_id, spotify_client_secret, download_dir, threads, cookie_file, cache_file):
        self.spotdl = Spotdl(
            client_id=spotify_client_id,
            client_secret=spotify_client_secret,
            user_auth=True,
            downloader_settings=DownloaderOptionalOptions(
                output=download_dir + "/{track-id}",
                format="opus",
                threads=threads,
                filter_results=False,
                cookie_file=cookie_file
            )
        )
        self.downloaded_song_ids = [file.stem for file in Path(download_dir).iterdir() if file.is_file()]
        self.cache_file = cache_file
        self.download_dir = download_dir

    def load_song_cache(self):
        try:
            with open(self.cache_file, "r") as f:
                songs_json = json.load(f)
                return [Song.from_dict(song_json) for song_json in songs_json]
        except FileNotFoundError:
            return []

    def fetch_song_data(self, extend_albums, cache=True):
        print("Fetching playlists from Spotify...")
        songs = get_simple_songs(["all-user-playlists"])
        print(f"Playlist songs: {len(songs)}")
        if extend_albums:
            albums = set(song.album_id for song in songs if song.album_id is not None)
            print(f"Albums: {len(albums)}")
            songs.extend(songs_from_albums(list(albums)))
            print(f"Songs extended by albums: {len(songs)}")

        dupe_filter = {}
        for song in songs:
            dupe_filter[song.url] = song

        songs = list(dupe_filter.values())
        if cache:
            with open(self.cache_file, "w") as f:
                json.dump([song.json for song in songs], f)
        return songs

    def download(self, songs):
        songs_to_download = [song for song in songs if song.song_id not in self.downloaded_song_ids]
        print(f"Songs up for download: {len(songs_to_download)}")
        self.spotdl.download_songs(songs_to_download)
