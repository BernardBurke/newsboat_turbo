#!/usr/bin/env python3
import json
import os
import sys
import datetime
import re
import subprocess
import urllib.request
import shutil

# --- Configuration ---
# The exact folder where your Audiobookshelf "Yodcasts" library lives
ABS_LIBRARY_BASE = "/media/abs_yodcasts"

def force_abs_cover_update(podcast_name, cover_path):
    """Reads ~/.abs_env and pushes the cover directly to the ABS API."""
    env_path = os.path.expanduser("~/.abs_env")
    env_vars = {}
    
    # 1. Load credentials (now safely handles "export" prefixes)
    if os.path.exists(env_path):
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if '=' in line and not line.startswith('#'):
                    # Strip 'export ' if it exists so we just get the key
                    if line.startswith("export "):
                        line = line[7:].strip()
                    k, v = line.split('=', 1)
                    env_vars[k.strip()] = v.strip().strip('"\'')
                    
    server_url = env_vars.get("AB_SERVER_URL", "http://127.0.0.1:13378").rstrip('/')
    api_key = env_vars.get("AB_API_KEY")
    lib_id = env_vars.get("AB_LIB_ID")

    if not api_key or not lib_id:
        print("⚠️ ABS API credentials not found in ~/.abs_env. Skipping API cover push.")
        return

    try:
        # 2. Query the Library to find the Podcast's internal ID
        print(f"🔍 Looking up internal ABS ID for podcast: {podcast_name}")
        req = urllib.request.Request(f"{server_url}/api/libraries/{lib_id}/items")
        req.add_header("Authorization", f"Bearer {api_key}")
        
        with urllib.request.urlopen(req) as response:
            data = json.loads(response.read())
            
        podcast_id = None
        for item in data.get("results", []):
            # Check if the ABS item matches our folder name
            if os.path.basename(item.get("path", "")) == podcast_name or \
               item.get("media", {}).get("metadata", {}).get("title") == podcast_name:
                podcast_id = item.get("id")
                break
                
        if not podcast_id:
            print(f"⚠️ Could not find '{podcast_name}' in ABS database yet. It might need a library scan first.")
            return

        # 3. Push the image directly via the API using curl multipart form
        print(f"🚀 Pushing new cover art to ABS API for item {podcast_id}...")
        post_cmd = [
            "curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", "-X", "POST",
            f"{server_url}/api/items/{podcast_id}/cover",
            "-H", f"Authorization: Bearer {api_key}",
            "-F", f"cover=@{cover_path}"
        ]
        
        post_result = subprocess.run(post_cmd, capture_output=True, text=True, check=True)
        if post_result.stdout.strip() == "200":
            print("✅ Cover art successfully updated and cached via API!")
        else:
            print(f"⚠️ API returned HTTP {post_result.stdout.strip()} when uploading cover.")

    except Exception as e:
        print(f"❌ Failed to push cover via API: {e}")

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
    
    # Clean folder name for the ABS Library
    clean_folder_name = re.sub(r'[^a-zA-Z0-9 ]', '', uploader).strip()
    author_dir = os.path.join(ABS_LIBRARY_BASE, clean_folder_name)
    os.makedirs(author_dir, exist_ok=True)
    
    final_audio_path = os.path.join(author_dir, f"{video_id}.m4a")
    input_ext = os.path.splitext(audio_path)[1].lower()
    audio_codec = "copy" if input_ext == ".m4a" else "aac"

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

    # 5. Handle Cover Art & Embed via FFmpeg
    try:
        valid_cover = False
        cover_art_path = os.path.join(author_dir, "cover.jpg")

        if thumb_url:
            if thumb_url.startswith("http://") or thumb_url.startswith("https://"):
                print(f"🖼️ Downloading new channel cover art: {thumb_url}")
                urllib.request.urlretrieve(thumb_url, cover_art_path)
                valid_cover = True
            elif os.path.exists(thumb_url):
                print(f"🖼️ Using local cover art file: {thumb_url}")
                shutil.copy2(thumb_url, cover_art_path)
                valid_cover = True
            else:
                print(f"⚠️ Warning: Could not resolve thumbnail path or URL: {thumb_url}")

        if valid_cover:
            print(f"🎬 Tagging and moving to {final_audio_path}...")
            cmd = [
                "ffmpeg", "-y", "-i", audio_path, "-i", cover_art_path,
                "-map", "0:a:0", "-map", "1:v:0",
                "-c:a", audio_codec, "-c:v:0", "png",
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
                "-c:a", audio_codec, 
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

        # Trigger the API Cover Update
        if valid_cover:
            force_abs_cover_update(clean_folder_name, cover_art_path)

    except subprocess.CalledProcessError as e:
        print(f"❌ FFmpeg error: {e.stderr.decode()}")
        if os.path.exists(final_audio_path):
            os.remove(final_audio_path)
    except Exception as e:
        print(f"❌ Error during processing: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 yt-to-local.py <path_to_info.json> <path_to_audio>")
        sys.exit(1)
        
    print(f"🚀 Starting local drop processing for: {sys.argv[2]}")
    process_and_move_audio(sys.argv[1], sys.argv[2])
    print("🏁 Python script finished successfully.")