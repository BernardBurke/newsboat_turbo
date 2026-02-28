#!/usr/bin/env bash

# Source our new library
U_PASTE="$LME/universal_paste.sh"
if [ -f "$U_PASTE" ]; then
    source "$U_PASTE"
else
    echo "❌ Error: Could not find universal_paste.sh"
    exit 1
fi

# Define your drop box location (change this to your SSHFS mount when remote)
QUEUE_FILE="$HOME/yodcast_drop/queue.txt"

echo "👀 Local Watcher started. Listening for YouTube links to queue..."

while true; do
    # This completely pauses the loop until a valid, NEW YouTube link is copied
    NEW_URL=$(wait_for_new_paste "youtube")
    
    echo "🔗 Caught new link: $NEW_URL"
    
    # Append to the queue file
    echo "$NEW_URL" >> "$QUEUE_FILE"
    echo "📥 Dropped into $QUEUE_FILE"
    
    # Notify the desktop
    notify-send "Yodcast Queued" "URL added to the drop box." --icon=emblem-default
done