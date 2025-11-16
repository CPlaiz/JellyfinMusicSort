#!/usr/bin/env python3
import os
import re
import shutil
from pathlib import Path

from mutagen.id3 import TXXX, ID3
from mutagen.oggopus import OggOpus
from mutagen.easyid3 import EasyID3

SPOTIFY_ID_RE = re.compile(r"^[A-Za-z0-9]{22}$")

def organize_audio_files(base_dir):
    # Make sure the base directory exists
    if not os.path.isdir(base_dir):
        print(f"Error: {base_dir} is not a directory.")
        return

    single_artist_songs = []
    multi_artist_songs = []

    # Walk through the directory and find Opus files
    for root, _, files in os.walk(base_dir):
        for file in files:
            file_path = os.path.join(root, file)
            stem = Path(file).stem
            spotify_id = stem if SPOTIFY_ID_RE.match(stem) else None
            try:
                if file.lower().endswith(".opus"):
                    tags = OggOpus(file_path)
                    if spotify_id:
                        tags["spotify_id"] = [spotify_id]
                    tags.save()
                elif file.lower().endswith(".mp3"):
                    tags = ID3(file_path)
                    if spotify_id:
                        tags.add(TXXX(encoding=3, desc="spotify_id", text=spotify_id))
                        tags.save()
                    tags = EasyID3(file_path)
                else:
                    continue

                artist = tags.get("artist", ["Unknown Artist"])[0]
                album = tags.get("album", ["Unknown Album"])[0]
                title = tags.get("title", [os.path.splitext(file)[0]])[0]

                item = (artist, album, title, file_path)
                if "," in artist:
                    multi_artist_songs.append(item)
                else:
                    single_artist_songs.append(item)

            except Exception as e:
                print(f"Skipping {file}: {e}")
                continue

    for (artist, album, title, file_path) in single_artist_songs:
        artist_dir = os.path.join(base_dir, sanitize_filename(artist))
        album_dir = os.path.join(artist_dir, sanitize_filename(album))

        os.makedirs(album_dir, exist_ok=True)

        # Move file
        new_file_path = os.path.join(album_dir, Path(file_path).name)
        if os.path.abspath(file_path) == os.path.abspath(new_file_path):
            continue  # Already in place

        if os.path.exists(new_file_path):
            print(f"File already exists: {new_file_path}, skipping.")
            continue

        print(f"Copying: {file_path} -> {new_file_path}")
        shutil.copy(file_path, new_file_path)

    for (artist, album, title, file_path) in multi_artist_songs:
        artists = [s.strip() for s in artist.split(",")]
        likely_album_artist = artists[0]

        for (single_artist, single_artist_album, _, _) in single_artist_songs:
            if single_artist == likely_album_artist:
                if album == single_artist_album:
                    artist_dir = os.path.join(base_dir, sanitize_filename(single_artist))
                    break
        else:
            artist_dir = os.path.join(base_dir, sanitize_filename(artist))

        album_dir = os.path.join(artist_dir, sanitize_filename(album))
        new_file_path = os.path.join(album_dir, Path(file_path).name)
        os.makedirs(album_dir, exist_ok=True)

        # Move file
        if os.path.abspath(file_path) == os.path.abspath(new_file_path):
            continue  # Already in place

        if os.path.exists(new_file_path):
            print(f"File already exists: {new_file_path}, skipping.")
            continue

        print(f"Copying: {file_path} -> {new_file_path}")
        shutil.copy(file_path, new_file_path)


def sanitize_filename(name):
    """Remove problematic characters for file and folder names."""
    return "".join(c for c in name if c not in '\\/:*?"<>|').strip()


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Organize Audio files by artist and album.")
    parser.add_argument("directory", help="Path to the directory containing Audio files")
    args = parser.parse_args()

    organize_audio_files(args.directory)
