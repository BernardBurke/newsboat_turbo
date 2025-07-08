#!/usr/bin/env bash
# if $1 is not set, exit
if [ -z "$1" ]; then
  echo "Usage: $0 <path_to_venv>"
  exit 1
fi  

# if $1 is a valid file, do this
if [  -f "$1" ]; then
  file_name=$(basename "$1" .html)
  tempfile="$1"
#else
# todo, parse the JSON for a title
# if [ -z "$tempfile" ]; then 
#   tempfile=$(mktemp)
#   curl -L "$1" -o "$tempfile"

#   if [ $? -ne 0 ]; then
#     echo "Failed to download the HTML file."
#     exit 1
#   fi

# fi  
  # AUDIO_JSON=$(yt-dlp -j "$1")  

  # title=$(echo "$AUDIO_JSON" | jq -r '.title')
  # title=$(echo "$title" | sed 's/[^[:alnum:] ]//g')
  # title=$(echo "$title" | sed 's/^[ \t]*//;s/[ \t]*$//')
  # echo "Title: $title"
  # file_name=$(echo "$title" | tr ' ' '_')  # replace spaces with underscores
  # # add .mp3 extension to the file name
  # file_name="${file_name}.mp3"
  
fi



# if $2 is a directory, use it as the output directory
if [ -d "$2" ]; then
  output_dir="$2"
else
  output_dir="."
fi

url=$(grep -oP 'audio_url\\":\\"\K(https?://.*?)\\"' $tempfile | sed 's/\\"$//' | head -n 1)

echo "Downloading audio from $url"

# use curl to download the audio file tot he output directory/file_name.mp3
curl -L "$url" -o "$output_dir/$file_name.mp3"  
if [ $? -eq 0 ]; then
  echo "Audio downloaded successfully to $output_dir/$file_name.mp3"
else
  echo "Failed to download audio."
  exit 1
fi