#!/usr/bin/env python3
import json
import os
import sys
import datetime
import re
import subprocess
import urllib.request

# --- Configuration ---
# The exact folder where your Audiobookshelf "Yodcasts" library lives
ABS_LIBRARY_BASE = "/media/abs_yodcasts"

def process_and_move_audio(json_path, audio_path):
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
    except Exception as e:
        print(f"❌ Error reading JSON: {e}")
        sys.exit(1)

    # 1. Bouncer Checks
    if data.get('is_live') is True:
        print("⚠️ Skipping active live stream.")
        sys.exit(0)

    if not os.path.exists(audio_path):
        print(f"❌ Error: Audio file missing at {audio_path}")
        sys.exit(1)

    # 2. Extract Metadata
    title = data.get('title', 'Unknown Title')
    uploader = data.get('uploader', 'Unknown Author')
    webpage_url = data.get('webpage_url', '')
    description = f"{data.get('description', '')}\n -- original_url: {webpage_url}"
    video_id = data.get('id', 'unknown_id')

    # Parse the exact YouTube upload date for Audiobookshelf
    raw_date = data.get('upload_date', datetime.datetime.now().strftime("%Y%m%d"))
    date_obj = datetime.datetime.strptime(raw_date, "%Y%m%d")
    pub_date = date_obj.strftime("%Y-%m-%d")  # Format: YYYY-MM-DD
    year = date_obj.strftime("%Y")            # Accurate release year
    
    # 3. Clean strings for ID3 tags and folder names
    clean_uploader_tag = re.sub(r'[^a-zA-Z0-9 ]', '', uploader).strip().replace(' ', '_')
    clean_title_tag = re.sub(r'[^a-zA-Z0-9 ]', '', title).strip()
    
    # Clean folder name for the ABS Library (e.g., "Sabine Hossenfelder")
    clean_folder_name = re.sub(r'[^a-zA-Z0-9 ]', '', uploader).strip()
    author_dir = os.path.join(ABS_LIBRARY_BASE, clean_folder_name)
    os.makedirs(author_dir, exist_ok=True)
    
    final_audio_path = os.path.join(author_dir, f"{video_id}.m4a")

    # 4. Find the best thumbnail
    thumb_url = None
    for t in data.get('thumbnails', []):
        if t.get('id') == 'mqdefault':
            thumb_url = t.get('url')
            break
        elif t.get('id') == 'medium' and not thumb_url:
            thumb_url = t.get('url')
    if not thumb_url:
        thumb_url = data.get('thumbnail')

    # 5. Embed via FFmpeg and output directly to the ABS library folder
    try:
        if thumb_url:
            print(f"🖼️ Downloading new channel cover art: {thumb_url}")
            # Shape-shifter hack: permanently save as cover.jpg to overwrite the channel image
            cover_art_path = os.path.join(author_dir, "cover.jpg")
            urllib.request.urlretrieve(thumb_url, cover_art_path)

            print(f"🎬 Tagging and moving to {final_audio_path}...")
            cmd = [
                "ffmpeg", "-y", "-i", audio_path, "-i", cover_art_path,
                "-map", "0:a:0", "-map", "1:v:0",
                "-c:a", "copy", "-c:v:0", "png",
                "-disposition:v:0", "attached_pic",
                "-metadata", f"title={clean_title_tag}",
                "-metadata", f"description={description}",
                "-metadata", f"artist={clean_uploader_tag}",
                "-metadata", f"album_artist={clean_uploader_tag}",
                "-metadata", f"album={clean_uploader_tag}",
                "-metadata", "genre=Podcast",
                "-metadata", f"year={year}",
                "-metadata", f"date={pub_date}", 
                "-metadata:s:v:0", "title=Album cover",
                "-metadata:s:v:0", "handler=Cover Art",
                final_audio_path
            ]
        else:
            print(f"⚠️ No cover art found. Tagging and moving to {final_audio_path}...")
            cmd = [
                "ffmpeg", "-y", "-i", audio_path,
                "-c", "copy",
                "-metadata", f"title={clean_title_tag}",
                "-metadata", f"description={description}",
                "-metadata", f"artist={clean_uploader_tag}",
                "-metadata", f"album_artist={clean_uploader_tag}",
                "-metadata", f"album={clean_uploader_tag}",
                "-metadata", "genre=Podcast",
                "-metadata", f"year={year}",
                "-metadata", f"date={pub_date}", 
                final_audio_path
            ]
        
        # Run FFmpeg
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, check=True)
        print("✅ Metadata embedding and file placement complete.")

    except subprocess.CalledProcessError as e:
        print(f"❌ FFmpeg error: {e.stderr.decode()}")
        if os.path.exists(final_audio_path):
            os.remove(final_audio_path)
    except Exception as e:
        print(f"❌ Error during processing: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 yt-to-local.py <path_to_info.json> <path_to_audio.m4a>")
        sys.exit(1)
        
    print(f"🚀 Starting local drop processing for: {sys.argv[2]}")
    process_and_move_audio(sys.argv[1], sys.argv[2])
    print("🏁 Python script finished successfully.")