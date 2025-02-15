#!/usr/bin/env bash
# read all the urls in $1 and call $NBT/nbt_ytdlp-audio-interface.sh for each one
# $1 is a file with one URL per line

if [[ "$1" == "" ]]; then
    echo "Please provide a file with URLs"
    exit 1
fi

while IFS= read -r url; do
    $NBT/nbt_ytdlp-vodcast-interface.sh "$url"
done < "$1"

# ask the user if they want to delete the file with the URLs
read -p "Delete the file with URLs? [y/N] " -n 1 -r
# if the user answers yes, delete the file
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm "$1"
fi
