#!/usr/bin/env bash
# The detox program is a great way 'normalise' filenames...
# As I write this, I've got some inconsistent folder names 
# which are "Podcast_Name" and "Podcast Name" (combo of yt-dlp and newsboat names)
#
# For now, I keep the folders without spaces in their names, using this 
# code drafted by Gemini
#!/bin/bash

main_folder="$Poddle"  # Replace with your main folder path

# Check if the main folder exists
if [[ ! -d "$main_folder" ]]; then
    echo "Main folder '$main_folder' not found"
    exit 1
fi


DRY_RUN=0  # Set to 1 to enable dry run mode

echo "Running on $Poddle in non-dry run mode"

# Function to handle a single space-containing folder
process_folder() {
    local space_folder="$1"
    underscore_folder="${space_folder// /_}"

    if [[ -d "$underscore_folder" ]]; then
        # Simulate moving files in dry run mode
        if [[ $DRY_RUN -eq 1 ]]; then
            echo "DRY RUN: Would move files from '$space_folder' to '$underscore_folder':"
            find "$space_folder" -type f -print
        else
            find "$space_folder" -type f -exec mv -vi {} "$underscore_folder" \;
        fi

        # Simulate deleting the folder in dry run mode
        if [[ $DRY_RUN -eq 1 ]]; then
            echo "DRY RUN: Would delete '$space_folder'"
        else
            rmdir -v "$space_folder"
        fi
    else
        echo "Parallel folder '$underscore_folder' not found for '$space_folder'"
    fi
}

# Find all space-containing folders within the main folder
find "$main_folder" -type d -name "* *" -print0 | 
    while IFS= read -r -d '' space_folder; do
        process_folder "$space_folder"
    done
