import os
import sys
import re
import json
import requests
from bs4 import BeautifulSoup
import yt_dlp
import tempfile

#!/usr/bin/env python3


def fetch_podcast_page(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text

def extract_podcast_info(url):
    podcast_id = re.search(r'id[0-9]+', url).group(0)
    podcast_name = re.search(r'(?<=/podcast/)[^/]+(?=/id[0-9]+)', url).group(0)
    return podcast_name, podcast_id

def extract_json_data(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    script_tag = soup.find('script', {'id': 'schema:show', 'type': 'application/ld+json'})
    if script_tag:
        return json.loads(script_tag.string)
    return None

def download_podcast_episodes(json_data, temp_dir):
    for item in json_data.get('workExample', []):
        if item.get('@type') == 'AudioObject':
            name = re.sub(r'[^a-zA-Z0-9]', '_', item.get('name', ''))
            url = item.get('url', '')
            if name and url:
                print(f"Downloading: {name} from {url}")
                ydl_opts = {'outtmpl': os.path.join(temp_dir, f"{name}.%(ext)s")}
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])

def main():
    if len(sys.argv) != 2:
        print("Please provide a Podcast URL")
        sys.exit(1)

    podcast_url = sys.argv[1]
    podcast_name, podcast_id = extract_podcast_info(podcast_url)
    print(f"Podcast ID: {podcast_id}")
    print(f"Podcast Name: {podcast_name}")

    html_content = fetch_podcast_page(podcast_url)
    with open(f"/tmp/{podcast_name}.html", 'w') as f:
        f.write(html_content)
    print(f"Saved to /tmp/{podcast_name}.html")

    json_data = extract_json_data(html_content)
    if json_data:
        temp_dir = tempfile.mkdtemp()
        download_podcast_episodes(json_data, temp_dir)
        print(f"Look in {temp_dir} for the downloaded files")
    else:
        print("No JSON data found in the page")

if __name__ == "__main__":
    main()
