#!/usr/bin/env python3
import os
from mutagen.easyid3 import EasyID3

def fix_artist_tags(base_dir):
    # Walk through all files in directory
    for root, _, files in os.walk(base_dir):
        for file in files:
            if not file.lower().endswith(".mp3"):
                continue

            file_path = os.path.join(root, file)
            try:
                tags = EasyID3(file_path)
            except Exception as e:
                print(f"Skipping {file}: {e}")
                continue

            # Check and fix artist tag
            if "artist" in tags:
                original = tags["artist"][0]
                fixed = original.replace("/", ", ")
                if fixed != original:
                    tags["artist"] = fixed
                    tags.save()
                    print(f"Updated artist: '{original}' → '{fixed}' in {file}")
            else:
                print(f"No artist tag found in {file}")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Replace '/' with ',' in MP3 artist tags.")
    parser.add_argument("directory", help="Path to the directory containing MP3 files")
    args = parser.parse_args()

    fix_artist_tags(args.directory)
