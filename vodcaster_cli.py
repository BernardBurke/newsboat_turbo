#!/usr/bin/env python3
import sys
import os
import readline # Improves input handling (history/arrow keys)
from vodcaster import VodcastDB

# CONFIGURATION
# The base URL where your files are hosted.
# If running locally for phone access, use your LAN IP (e.g., http://192.168.1.X:8000)
DEFAULT_HOST = "http://192.168.1.50:8000"

def get_input(prompt, default=None):
    """Helper for nice prompts with defaults"""
    text = f"{prompt}"
    if default:
        text += f" [{default}]"
    text += ": "
    val = input(text).strip()
    return val if val else default

def main():
    # Initialize connection to DB (will create vodcasts.db if missing)
    db = VodcastDB()
    
    while True:
        print("\n--- Vodcast Manager ---")
        print("1. Create New Vodcast Feed")
        print("2. Add Episode to Existing Feed")
        print("3. Regenerate All RSS Feeds")
        print("4. Exit")
        
        choice = input("Select option: ").strip()

        if choice == '1':
            print("\n--- Create New Feed ---")
            title = get_input("Friendly Name (e.g., 'Nebula Rips')")
            desc = get_input("Description", "My local collection")
            link = get_input("Original Source URL (optional)", "")
            base_url = get_input("Base Host URL", DEFAULT_HOST)
            
            pid = db.create_podcast(title, desc, link, base_url)
            if pid:
                print("Feed created!")

        elif choice == '2':
            # List Podcasts
            pods = db.get_podcasts()
            if not pods:
                print("No feeds exist yet. Create one (Option 1) first.")
                continue

            print("\n--- Select Feed ---")
            for p in pods:
                print(f"{p['id']}: {p['title']} ({p['slug']}.xml)")
            
            try:
                pid_input = input("Enter Feed ID: ").strip()
                if not pid_input: continue
                pid = int(pid_input)
                
                selected_pod = db.get_podcast_by_id(pid)
                if not selected_pod: raise ValueError
            except ValueError:
                print("Invalid ID.")
                continue

            # File Selection
            # This handles arguments passed to the script OR prompts
            if len(sys.argv) > 1 and os.path.exists(sys.argv[1]):
                fpath = sys.argv[1]
                print(f"Using file from argument: {fpath}")
                # Clear argv so the loop doesn't re-add the same file next time
                sys.argv = [] 
            else:
                fpath = get_input("Path to media file").strip("'\"")

            if not os.path.exists(fpath):
                print(f"Error: File not found at {fpath}")
                continue

            # Metadata Entry
            default_title = os.path.splitext(os.path.basename(fpath))[0].replace('_', ' ')
            ep_title = get_input("Episode Title", default_title)
            ep_desc = get_input("Episode Description", "")
            
            # Add to DB
            db.add_episode(pid, fpath, ep_title, ep_desc)
            
            # Regenerate RSS immediately so it's ready to fetch
            db.generate_rss(pid)

        elif choice == '3':
            pods = db.get_podcasts()
            if not pods:
                print("No podcasts found.")
            else:
                for p in pods:
                    db.generate_rss(p['id'])
                print("All feeds updated.")

        elif choice == '4':
            print("Exiting.")
            break

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nExiting.")