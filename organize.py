#!/usr/bin/env python3
import os
import shutil
from mutagen.easyid3 import EasyID3


def organize_mp3s(base_dir):
    # Make sure the base directory exists
    if not os.path.isdir(base_dir):
        print(f"Error: {base_dir} is not a directory.")
        return

    single_artist_songs = []
    multi_artist_songs = []

    # Walk through the directory and find MP3 files
    for root, _, files in os.walk(base_dir):
        for file in files:
            if not file.lower().endswith(".mp3"):
                continue

            file_path = os.path.join(root, file)
            try:
                tags = EasyID3(file_path)
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
        new_file_path = os.path.join(album_dir, sanitize_filename(f"{title}.mp3"))
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
        new_file_path = os.path.join(album_dir, sanitize_filename(f"{title}.mp3"))
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

    parser = argparse.ArgumentParser(description="Organize MP3 files by artist and album.")
    parser.add_argument("directory", help="Path to the directory containing MP3 files")
    args = parser.parse_args()

    organize_mp3s(args.directory)
