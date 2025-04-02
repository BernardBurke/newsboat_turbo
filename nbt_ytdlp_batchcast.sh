#!/bin/bash
# Your script: $NBT/nbt_ytdlp-vodcast-interface.sh

# --- Start Logging ---
# Use an absolute path for reliability first
LOG_FILE="/home/ben/nbt_script_internal.log"

# Redirect stdout (fd 1) and stderr (fd 2) to the log file, appending
# The exec command replaces the script's current stdout/stderr for the rest of its execution
exec >> "$LOG_FILE" 2>&1
# --- End Logging Setup ---

# --- Start of your actual script logic ---
echo "----------------------------------------" # Separator for log entries
echo "Script started: $(date)"
echo "Newsboat Version (if available): $NEWSBOAT_VERSION" # Newsboat might set this env var
echo "Received URL: $1" # $1 is the first argument (the URL passed from Newsboat)

# Add your actual commands here (e.g., yt-dlp)
# Any output (echo) or errors from these commands will now go to $LOG_FILE
echo "Running yt-dlp command..."
yt-dlp --quiet --print "%(title)s" "$1" # Example yt-dlp command - adjust as needed

# Add more commands or logic as required...

echo "Script finished: $(date)"
echo "----------------------------------------"
echo "" # Add a blank line for separation in the log