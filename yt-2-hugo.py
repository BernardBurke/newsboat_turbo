#!/usr/bin/env python3
import json
import os
import sys
import datetime
import re
import subprocess
import urllib.request
import tempfile
import shutil

# --- Configuration ---
HUGO_PODCAST_BASE = "/home/ben/projects/personal/self_rss/content/podcasts"
BASE_MEDIA_URL = "https://media.benburke.dev/yodcasts"
# The absolute fallback image if scraping fails completely (a generic microphone)
DEFAULT_COVER_ART = "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Microphone_icon.svg/1024px-Microphone_icon.svg.png"

def embed_ffmpeg_metadata(audio_path, data):
    """Replicates the Bash ffmpeg embedding logic."""
    if not os.path.exists(audio_path):
        print("Audio file missing, skipping ffmpeg embedding.")
        return

    # 1. Extract Metadata for FFmpeg
    title = data.get('title', 'Unknown Title')
    uploader = data.get('uploader', 'Unknown Author')
    webpage_url = data.get('webpage_url', '')
    description = f"{data.get('description', '')}\n -- original_url: {webpage_url}"
    year = str(datetime.datetime.now().year)

    # Clean strings for metadata (basic alphanumeric + space stripping)
    clean_uploader = re.sub(r'[^a-zA-Z0-9 ]', '', uploader).strip().replace(' ', '_')
    clean_title = re.sub(r'[^a-zA-Z0-9 ]', '', title).strip()

    # 2. Find the best thumbnail (matching your bash logic)
    thumb_url = None
    for t in data.get('thumbnails', []):
        if t.get('id') == 'mqdefault':
            thumb_url = t.get('url')
            break
        elif t.get('id') == 'medium' and not thumb_url:
            thumb_url = t.get('url')
    
    if not thumb_url:
        thumb_url = data.get('thumbnail')

    # 3. Setup Temporary Files
    temp_audio = audio_path + ".temp.m4a"
    thumb_path = None

    try:
        if thumb_url:
            print(f"Downloading thumbnail for embedding: {thumb_url}")
            with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tf:
                thumb_path = tf.name
            urllib.request.urlretrieve(thumb_url, thumb_path)

            print("Attaching downloaded thumbnail as album art via FFmpeg...")
            cmd = [
                "ffmpeg", "-y", "-i", audio_path, "-i", thumb_path,
                "-map", "0:a:0", "-map", "1:v:0",
                "-c:a", "copy", "-c:v:0", "png",
                "-disposition:v:0", "attached_pic",
                "-metadata", f"title={clean_title}",
                "-metadata", f"description={description}",
                "-metadata", f"artist={clean_uploader}",
                "-metadata", f"album_artist={clean_uploader}",
                "-metadata", f"album={clean_uploader}",
                "-metadata", "genre=Podcast",
                "-metadata", f"year={year}",
                "-metadata:s:v:0", "title=Album cover",
                "-metadata:s:v:0", "handler=Cover Art",
                temp_audio
            ]
        else:
            print("No thumbnail found. Embedding metadata without cover art...")
            cmd = [
                "ffmpeg", "-y", "-i", audio_path,
                "-c", "copy",
                "-metadata", f"title={clean_title}",
                "-metadata", f"description={description}",
                "-metadata", f"artist={clean_uploader}",
                "-metadata", f"album_artist={clean_uploader}",
                "-metadata", f"album={clean_uploader}",
                "-metadata", "genre=Podcast",
                "-metadata", f"year={year}",
                temp_audio
            ]
        
        # Run FFmpeg quietly
        subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, check=True)
        
        # Replace original audio with the tagged version
        shutil.move(temp_audio, audio_path)
        print("FFmpeg metadata embedding complete.")

    except subprocess.CalledProcessError as e:
        print(f"FFmpeg error: {e.stderr.decode()}")
        if os.path.exists(temp_audio):
            os.remove(temp_audio)
    except Exception as e:
        print(f"Error during embedding: {e}")
    finally:
        if thumb_path and os.path.exists(thumb_path):
            os.remove(thumb_path)

def generate_hugo_md(json_path, audio_path):
    try:
        with open(json_path, 'r') as f:
            data = json.load(f)
    except Exception as e:
        print(f"Error reading JSON: {e}")
        sys.exit(1)

    # Detect live streams and skip them
    if data.get('is_live') is True:
        print("Skipping live stream.")
        sys.exit(0)

    # Execute the FFmpeg tagging before calculating file size
    embed_ffmpeg_metadata(audio_path, data)

    # Core Metadata for Hugo
    title = data.get('title', 'Unknown Title').replace('"', '\\"')
    video_id = data.get('id', 'unknown_id')
    thumbnail = data.get('thumbnail', DEFAULT_COVER_ART)
    author = data.get('uploader', 'Unknown Author').replace('"', '\\"')
    duration = data.get('duration', 0)
    
    # Date Handling
    raw_date = data.get('upload_date', datetime.datetime.now().strftime("%Y%m%d"))
    date_obj = datetime.datetime.strptime(raw_date, "%Y%m%d")
    iso_date = date_obj.strftime("%Y-%m-%dT12:00:00Z")

    # Clean Description for Hugo Front Matter
    raw_desc = data.get('description', 'No description available.')
    short_desc = raw_desc.split('\n')[0].replace('"', '\\"').strip()
    if len(short_desc) > 250:
        short_desc = short_desc[:247] + "..."

    # Audio File Handling
    audio_filename = os.path.basename(audio_path)
    audio_url = f"{BASE_MEDIA_URL}/{audio_filename}"
    audio_size = os.path.getsize(audio_path) if os.path.exists(audio_path) else 0

    # Channel Folder Logic
    author_slug = re.sub(r'[^a-zA-Z0-9]+', '-', author).strip('-').lower()
    channel_dir = os.path.join(HUGO_PODCAST_BASE, author_slug)
    os.makedirs(channel_dir, exist_ok=True)

    # Auto-generate _index.md with Avatar Scraper
    index_path = os.path.join(channel_dir, "_index.md")
    if not os.path.exists(index_path):
        print(f"New channel detected! Scraping high-res avatar for '{author}'...")
        channel_url = data.get('channel_url')
        avatar_url = DEFAULT_COVER_ART
        
        channel_url = data.get('channel_url') or data.get('uploader_url')
        if channel_url:
            try:
                # Use --dump-single-json to force the channel dict to print
                cmd = ["yt-dlp", "--dump-single-json", "--playlist-items", "0", channel_url]
                result = subprocess.run(cmd, capture_output=True, text=True, check=True)
                channel_data = json.loads(result.stdout)        
                # yt-dlp puts channel avatars in the thumbnails array. Grab the highest res.
                thumbnails = channel_data.get('thumbnails', [])
                if thumbnails:
                    avatar_url = thumbnails[-1].get('url', DEFAULT_COVER_ART)
                    print("Successfully grabbed real channel avatar.")
            except Exception as e:
                print(f"Warning: Could not fetch channel avatar. Using default. Error: {e}")

        index_content = f"""---
title: "{author}"
description: "Automated archive of the {author} YouTube channel."
itunes_author: "{author}"
itunes_image: "{avatar_url}"
type: "podcasts"
---
"""
        with open(index_path, 'w') as f:
            f.write(index_content)

    # Write Episode File
    md_content = f"""---
title: "{title}"
date: {iso_date}
draft: false
description: "{short_desc}"
podcast_audio: "{audio_url}"
podcast_bytes: "{audio_size}"
podcast_duration: "{duration}"
itunes_author: "{author}"
itunes_image: "{thumbnail}"
---
"""
    
    out_path = os.path.join(channel_dir, f"{video_id}.md")
    with open(out_path, 'w') as f:
        f.write(md_content)
        
    print(f"Success! Created episode: {out_path}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 yt-to-hugo.py <path_to_info.json> <path_to_audio.m4a>")
        sys.exit(1)
        
    json_input = sys.argv[1]
    audio_input = sys.argv[2]
    generate_hugo_md(json_input, audio_input)