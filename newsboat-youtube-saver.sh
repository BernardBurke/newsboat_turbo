#!/bin/bash

# Get the current date in YYYY-MM-DD format
CURRENT_DATE=$(date +%Y-%m-%d)

# Define the path to your log file, incorporating the date
# Example: $HOME/newsboat_youtube_urls_2025-11-28.txt
LOG_FILE="$HOME/newsboat_youtube_urls_$CURRENT_DATE.txt"

# The URL is passed as the first argument from Newsboat (%u)
YOUTUBE_URL="$1"

# Check if the URL is provided
if [ -z "$YOUTUBE_URL" ]; then
    echo "Error: No URL provided."
    exit 1
fi

# Append the URL and a newline character to the daily log file.
# If the file for today doesn't exist, it will be created.
echo "$YOUTUBE_URL" >> "$LOG_FILE"

# Exit with 1 to prevent Newsboat from opening the browser for the script's output,
# effectively stopping the macro after saving the URL.
exit 1
