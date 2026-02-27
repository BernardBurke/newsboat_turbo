#!/usr/bin/env bash
source "$LME/universal_paste.sh"

echo "Watching clipboard for YouTube links... (Ctrl+C to stop)"

LAST_URL=$(get_pasted_input)

while true; do
    # 1. Grab current clipboard
    CURRENT_CONTENT=$(get_pasted_input)

    # 2. If it's a NEW YouTube link we haven't processed yet
    if [[ "$CURRENT_CONTENT" != "$LAST_URL" ]]; then
        if validate_input "$CURRENT_CONTENT" "youtube"; then
            echo 
            
            notify-send "YouTube Watcher" "🚀 New Link Detected: $CURRENT_CONTENT writing queue file..." --icon=video-x-generic

            # 3. write queue file
            QUEUE_FILE="$HOME/yodcast_drop/queue.txt"
        
            # Append the URL to the queue file
            echo "$LAST_URL" >> "$QUEUE_FILE"
            echo "📥 Dropped into local queue!"
                
            # 4. Update LAST_URL so we don't download the same thing twice
            LAST_URL="$CURRENT_CONTENT"
        fi
    fi

    # 5. Wait 2 seconds before checking again to save CPU
    sleep 2
done
