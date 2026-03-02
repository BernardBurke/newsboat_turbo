#!/usr/bin/env bash

# Source our new library
U_PASTE="$LME/universal_paste.sh"
YOD_ONE="$LME/yod_one.sh"

if [ -f "$U_PASTE" ]; then
    source "$U_PASTE"
else
    echo "❌ Error: Could not find universal_paste.sh"
    exit 1
fi

# ==========================================
# SYSTEM TRAY ICON SETUP
# ==========================================
cleanup() {
    echo "🛑 Shutting down Direct Watcher..."
    [[ -n "$TRAY_PID" ]] && kill "$TRAY_PID" 2>/dev/null
    exit 0
}
trap cleanup INT TERM EXIT

yad --notification \
    --image="emblem-downloads" \
    --text="Direct Yodcast Watcher: ON\nClick to stop." \
    --command="kill -TERM $$" 2>/dev/null &
TRAY_PID=$!
# ==========================================

echo "👀 Direct Watcher started. Listening for YouTube links to download..."

while true; do
    # Pause the loop until a valid, NEW YouTube link is copied
    NEW_URL=$(wait_for_new_paste "youtube")
    
    echo "🔗 Caught new link: $NEW_URL"
    notify-send "Yodcast Started" "Firing up the download engine..." --icon=emblem-default
    
    # Execute the download engine directly
    "$YOD_ONE" "$NEW_URL"
done