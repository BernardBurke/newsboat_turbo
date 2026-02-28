#!/usr/bin/env bash

# Source our library from the Linux Mint Environment directory
if [ -f "$LME/universal_paste.sh" ]; then
    source "$LME/universal_paste.sh"
else
    echo "❌ Error: Could not find universal_paste.sh in \$LME"
    exit 1
fi

# ==========================================
# Helper: Extract Video ID and Timestamp
# Uses the exact regex from your universal_paste.md specs!
# ==========================================
parse_url() {
    local url="$1"
    local id=$(echo "$url" | grep -oP '(?<=v=)[^&]+|(?<=youtu\.be/)[^?]+' | head -n 1)
    local time=$(echo "$url" | grep -oP 't=\K[0-9]+' | head -n 1)
    echo "$id $time"
}

echo "✂️ Precision Clipper Watcher Started."
echo "Waiting for you to Right-Click -> 'Copy video URL at current time' twice..."

while true; do
    # ------------------------------------------
    # 1. Grab the First Point
    # ------------------------------------------
    URL1=$(wait_for_new_paste "youtube")
    read ID1 T1 <<< $(parse_url "$URL1")

    if [ -z "$T1" ]; then
        echo "⚠️ No timestamp found in URL. Ignoring..."
        continue
    fi

    echo "📍 Point 1 marked at ${T1}s for video $ID1."
    notify-send "Clip Point 1" "Marked at ${T1}s. Copy the second timestamp." --icon=media-playback-start

    # ------------------------------------------
    # 2. Grab the Second Point
    # ------------------------------------------
    URL2=$(wait_for_new_paste "youtube")
    read ID2 T2 <<< $(parse_url "$URL2")

    if [ -z "$T2" ]; then
        echo "⚠️ No timestamp found in second URL. Resetting..."
        continue
    fi

    # ------------------------------------------
    # 3. Bouncer Checks & Math
    # ------------------------------------------
    if [ "$ID1" != "$ID2" ]; then
        echo "❌ Error: Video IDs do not match ($ID1 vs $ID2). Resetting..."
        notify-send "Clip Error" "Video IDs didn't match. Start over." --icon=dialog-error
        continue
    fi

    # Auto-sort the timestamps so you can copy in any order
    if [ "$T1" -lt "$T2" ]; then
        START=$T1
        END=$T2
    else
        START=$T2
        END=$T1
    fi

    # ------------------------------------------
    # 4. The Extraction Engine
    # ------------------------------------------
    OUT_FILE="/tmp/${ID1}_${START}_${END}.mp4"
    
    echo "✂️ Clipping $ID1 from ${START}s to ${END}s..."
    notify-send "Clipping Started" "Extracting ${START}s to ${END}s..." --icon=media-record

    # Using -f 18 (360p mp4) per your request, with native section downloading
   # Using -f 18 (360p mp4) per your request, with native section downloading
    yt-dlp -f 18 \
        --download-sections "*${START}-${END}" \
        --force-keyframes-at-cuts \
        --no-warnings \
        --downloader-args "ffmpeg:-hide_banner -loglevel error" \
        -o "$OUT_FILE" \
        "https://www.youtube.com/watch?v=${ID1}"

    if [ -f "$OUT_FILE" ]; then
        echo "======================================"
        echo "✅ Clip successfully saved to:"
        echo "📂 $OUT_FILE"
        echo "======================================"
        notify-send "Clip Complete!" "Saved to /tmp" --icon=emblem-default
    else
        echo "❌ Failed to generate clip."
        notify-send "Clip Failed" "Check terminal output." --icon=dialog-error
    fi
    
    echo "Ready for the next clip..."
done