#!/bin/bash

# --- Configuration & Initial Checks ---

if [[ "$1" == "" ]]; then
	echo "Please provide a URL"
	exit 1
fi

# Determine PODPATH
if [[ "$PODPATH" != "" ]]; then
	echo "PODPATH set externally to $PODPATH"
else
	# Use a safe default directory path
	PODPATH="$HOME/Vodcasts"
fi

# Log the current operation
echo "$(date) $1" >> "$HOME/yix_data.log"

# --- Fetch Video Metadata ---

# Fetch video metadata as JSON using yt-dlp
VIDEO_JSON=$(yt-dlp -j "$1")
if [ $? -ne 0 ]; then
    echo "Error: yt-dlp failed to fetch JSON metadata."
    exit 1
fi

# Extract metadata using jq and clean strings
uploader=$(echo "$VIDEO_JSON" | jq -r '.uploader')
uploader=$(echo "$uploader" | sed 's/[^[:alnum:] ]//g' | sed 's/^[ \t]*//;s/[ \t]*$//' | sed 's/ /_/g')
echo "Uploader: $uploader"

title=$(echo "$VIDEO_JSON" | jq -r '.title')
title=$(echo "$title" | sed 's/[^[:alnum:] ]//g' | sed 's/^[ \t]*//;s/[ \t]*$//')
echo "Title: $title"

ext=$(echo "$VIDEO_JSON" | jq -r '.ext')
echo "Original file extension: $ext"

description=$(echo "$VIDEO_JSON" | jq -r '.description')
# Add a line break and the original URL to the description
description="$description 
 -- original_url: $1"
echo "Description: $description"

# --- Thumbnail Extraction and Download ---

# 1. Try to find the 'mqdefault' thumbnail URL specifically
THUMBNAIL_URL=$(echo "$VIDEO_JSON" | jq -r '.thumbnails[] | select(.id == "mqdefault") | .url')

# 2. Fallback to 'medium' if 'mqdefault' isn't explicitly an ID (often the same)
if [ -z "$THUMBNAIL_URL" ]; then
    THUMBNAIL_URL=$(echo "$VIDEO_JSON" | jq -r '.thumbnails[] | select(.id == "medium") | .url')
fi

# 3. Fallback to the main 'thumbnail' key if specific IDs are missing
if [ -z "$THUMBNAIL_URL" ]; then
    THUMBNAIL_URL=$(echo "$VIDEO_JSON" | jq -r '.thumbnail')
fi

# Define temporary file for the downloaded thumbnail image
THUMBNAIL_FILE="/tmp/yt_cover_$(date +%s%N).jpg"

echo "Thumbnail URL: $THUMBNAIL_URL"
echo "Downloading thumbnail to: $THUMBNAIL_FILE"

# Download the thumbnail image using curl
if curl -s -L -o "$THUMBNAIL_FILE" "$THUMBNAIL_URL"; then
    echo "Thumbnail downloaded successfully."
else
    echo "Warning: Thumbnail download failed. Proceeding without cover art."
    THUMBNAIL_FILE="" # Clear file path if download fails
fi

# --- Setup Output Paths ---

OUTPUT_FILENAME="$PODPATH/$uploader/$title.m4a"
PODTEMPSTRING="/tmp/$uploader/$title.m4a" # Temporary file for audio download

# Create directory if it doesn't exist
if [ ! -d "$PODPATH/$uploader" ]; then
	mkdir -p "$PODPATH/$uploader"
fi

# --- Download Audio ---

echo "Downloading best audio (m4a) to $PODTEMPSTRING"
if yt-dlp -f 'bestaudio[ext=m4a]' "$1" -o "$PODTEMPSTRING"; then
	echo "Download complete"
else
	echo "Download failed - saving URL to $HOME/yix__error_data.log"
	echo "$1" >> "$HOME/yix__error_data.log"
    # Attempt a second try
    if yt-dlp -f 'bestaudio[ext=m4a]' "$1" -o "$PODTEMPSTRING"; then
		echo "Download completed on second try"
	else
		echo "Download failed again"
		echo "$1" >> "$HOME/yix__error_data.log"
	fi
	exit 1
fi

# --- Update Metadata and Embed Cover Art ---

echo "Updating metadata and embedding cover art"

if [[ ! -f "$PODTEMPSTRING" ]]; then
	echo "Error: Audio file not found at $PODTEMPSTRING. Exiting."
	exit 1
fi

if [ -f "$THUMBNAIL_FILE" ]; then
    # Robust method: Use the downloaded thumbnail as a second input stream (1)
    # and map it to the video stream (v:0) using PNG codec for M4A/MP4 compatibility.
    echo "Attaching downloaded thumbnail as album art."
    ffmpeg -i "$PODTEMPSTRING" -i "$THUMBNAIL_FILE" \
        -map 0:a:0 -map 1:v:0 \
        -c:a copy \
        -c:v:0 png \
        -disposition:v:0 attached_pic \
        -metadata title="$title" \
        -metadata description="$description" \
        -metadata artist="$uploader" \
        -metadata album_artist="$uploader" \
        -metadata album="$uploader" \
        -metadata genre="Podcast" \
        -metadata year="$(date +%Y)" \
        -metadata:s:v:0 title="Album cover" \
        -metadata:s:v:0 handler="Cover Art" \
        "$OUTPUT_FILENAME"
    
    # Clean up temporary thumbnail file
    rm -f "$THUMBNAIL_FILE"
else
    # Fallback: simple metadata update without cover art
    echo "Embedding metadata without cover art (thumbnail file missing)."
    ffmpeg -i "$PODTEMPSTRING" -c copy \
        -metadata title="$title" \
        -metadata description="$description" \
        -metadata artist="$uploader" \
        -metadata album_artist="$uploader" \
        -metadata album="$uploader" \
        -metadata genre="Podcast" \
        -metadata year="$(date +%Y)" \
        "$OUTPUT_FILENAME"
fi

# Clean up temporary audio file
rm -f "$PODTEMPSTRING"

echo "Processing complete. Final file saved to $OUTPUT_FILENAME"
# log the $1 and $OUTPUT_FILENAME to a file in $HOME called yix_data.log
echo "$1" "$OUTPUT_FILENAME" >> "$HOME/yix_data.log"

# You can re-enable your detox line if needed:
# detox -v "$PODPATH/$uploader/"