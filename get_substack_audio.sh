#!/usr/bin/env bash
# if $1 is not set, exit
if [ -z "$1" ]; then
  echo "Usage: $0 <path_to_html>"
  exit 1
fi  

# if $2 is a directory, use it as the output directory
if [ -d "$2" ]; then
  output_dir="$2"
  echo "Using output directory: $output_dir"
else
  output_dir="/tmp"
  echo "Output directory not specified or invalid. Using /tmp."
fi



# # This function takes a filename $1 and target directory $2. We remove any special characters from the filename and move it to the target directory.
# sanitize_and_move() {
#   local filename="$1"
#   local target_dir="$2"

# # check that these are both valid
#     if [ ! -f "$filename" ]; then
#         echo "File $filename does not exist or is not a valid file."
#         exit 1
#     fi
#     if [ ! -d "$target_dir" ]; then
#             echo "Target directory $target_dir does not exist or is not a valid directory."
#             exit 1
#     fi
#     directory_name=$(dirname "$filename")
#     just_the_file_name=$(basename "$filename" .html)

# # sanitize the filename by removing special characters
#     local sanitized_filename=$(echo "$just_the_file_name" | sed 's/[^[:alnum:]_ -]//g' | sed 's/ /_/g')
#     local sanitized_filename=${directory_name}/${sanitized_filename}
#     local new_file_path="$target_dir/$sanitized_filename"
#     # move the file to the target directory with the sanitized name
#     mv "$filename" "$new_file_path"
#     echo "The working file path is : $new_file_path"
# }

  # Remove special characters from the filename



# if $1 is a valid file, do this
if [  -f "$1" ]; then
  echo "File $1 exists. Detoxing."
 # cleaned_file=$(detox_rename "$1" "$output_dir")
    directory_name="$(dirname "$1")"
    filename_only="$(basename "$1" .html)"
    cleaned_file="$(echo "$filename_only" | sed 's/[^[:alnum:]_ -]//g' | sed 's/ /_/g')"
    clean_destination="${output_dir}/${cleaned_file}.html"
    echo "Cleaned destination file name: $clean_destination" 
    mv "$1" "$clean_destination" -v
    audio_file_destination="${output_dir}/${cleaned_file}.mp3"
    echo "Audio file destination: $audio_file_destination"
else
  echo "File $1 does not exist or is not a valid file."
  exit 1
fi





#url=$(grep -oP 'audio_url\\":\\"\K(https?://.*?)\\"' $cleaned_file | sed 's/\\"$//' | head -n 1)
url=$(grep -oP 'audio_url\\":\\"\K(https?://.*?)\\"' $clean_destination | sed 's/\\"$//' | head -n 1)

echo "Downloading audio from $url"

# use curl to download the audio file tot he output directory/file_name.mp3
curl -L "$url" -o "$audio_file_destination"  
if [ $? -eq 0 ]; then
  echo "Audio downloaded successfully to $audio_file_destination"
else
  echo "Failed to download audio."
  exit 1
fi
