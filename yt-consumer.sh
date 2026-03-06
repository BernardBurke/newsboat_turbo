#!/usr/bin/env bash

exec {lock_fd}>/tmp/yodcast_consumer.lock || exit 1
flock -n "$lock_fd" || { echo "⚠️ Consumer already running. Exiting."; exit 0; }

DROP_DIR="$HOME/yodcast_drop"
QUEUE_FILE="$DROP_DIR/queue.txt"
WORK_FILE="$DROP_DIR/processing.txt"
YOD_ONE="$LME/yod_one.sh"

echo "🎧 Odetta Consumer listening on $DROP_DIR..."

while true; do
    if [ -s "$QUEUE_FILE" ]; then
        echo "📦 Found new URLs in queue! Snatching file..."
        
        # Atomic move: Instantly renames the file so the watcher 
        # can safely start a brand new queue.txt on the next copy.
        mv "$QUEUE_FILE" "$WORK_FILE"
        
        # Feed the batch file to your existing engine
        "$YOD_ONE" "$WORK_FILE"
        
        # Clean up
        rm -f "$WORK_FILE"
        echo "✨ Queue processed. Back to sleep..."
    fi
    
    # Check the folder every 10 seconds
    sleep 10
done
