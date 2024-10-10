#!/usr/bin/env bash

# This script takes one argument - an apple podcasts url, that looks like this example:
# https://podcasts.apple.com/us/podcast/the-losers-club-a-stephen-king-podcast/id1269139179

# The script will extract the podcast name and the podcast id from the url
# and then use the podcast id to download the podcast feed in JSON format
# and then extract the podcast author and the podcast name from the JSON
# and then use the podcast author and the podcast name to create a folder
# and then use the podcast name to create a file name
# and then download the podcast feed in JSON format
# and then extract the podcast episodes from the JSON
# and then download the podcast episodes

# The script will also log the podcast url, the podcast author, the podcast name, the podcast id, the podcast feed url, the podcast feed author, the podcast feed name, the podcast feed episodes, the podcast episode url, the podcast episode author, the podcast episode name, the podcast episode id, the podcast episode file name, the podcast episode file path, the podcast episode file url, the podcast episode file size, the podcast episode file duration, the podcast episode file type, the podcast episode file format, the podcast episode file codec, the podcast episode file bitrate, the podcast episode file sample rate, the podcast episode file channels, the podcast episode file language, the podcast episode file license, the podcast episode file description, the podcast episode file tags, the podcast episode file date, the podcast episode file time, the podcast episode file year, the podcast episode file month, the podcast episode file day, the podcast episode file hour, the podcast episode file minute, the podcast episode file second, the podcast episode file millisecond, the podcast episode file timezone, the podcast episode file offset, the podcast episode file duration hours, the podcast episode file duration minutes, the podcast episode file duration seconds, the podcast episode file duration milliseconds, the podcast episode file duration timezone, the podcast episode file duration offset, the podcast episode file duration hours, the podcast episode file duration minutes, the podcast episode file duration seconds, the podcast episode file duration milliseconds, the podcast episode file duration timezone, the podcast episode file duration offset, the podcast episode file duration hours, the podcast episode file duration minutes, the podcast episode file duration seconds, the podcast episode file duration milliseconds, the podcast episode file duration timezone, the podcast episode file duration offset, the podcast episode file duration hours, the podcast episode file duration minutes, the podcast episode file duration seconds, the podcast episode file duration milliseconds, the podcast episode file duration timezone, the podcast episode file duration offset, the podcast episode file duration hours, the podcast episode file duration minutes, the podcast episode file duration seconds, the podcast episode file duration milliseconds, the podcast episode file duration timezone, the podcast episode file duration offset, the podcast episode file duration hours, the podcast episode file duration minutes, the podcast episode file duration seconds, the podcast episode file duration milliseconds, the podcast episode file duration timezone, the podcast episode file duration offset, the podcast episode file duration hours, the podcast episode file duration minutes, the podcast episode file duration seconds, the podcast episode file duration milliseconds


# Check if the script has been provided with an argument
if [[ "$1" == "" ]]; then
    echo "Please provide a Podcast URL"
    exit 1
fi

# get the ID from the URL
PODCAST_ID=$(echo "$1" | grep -oP 'id[0-9]+')
echo "Podcast ID: $PODCAST_ID"
# PODCAST_NAME occurs between /podcast/ and /id
# Get the podcast name
PODCAST_NAME=$(echo "$1" | grep -oP '(?<=/podcast/)[^/]+(?=/id[0-9]+)')
echo "Podcast Name: $PODCAST_NAME"

# Set the main folder path
PODDLE=~/Poddle

TMP=$(mktemp)
echo "Fetching $1"

echo "Raw page:"
wget -qO- "$1"  > "$TMP"
#cat $TMP
cp $TMP  /tmp/${PODCAST_NAME}.html
echo "Saved to /tmp/$PODCAST_NAME.html"

# search /tmp/$PODCAST_NAME.html for json contained between <script id=schema:show type="application/ld+json"> and </script>
# and write it to screen



#grep -oE '<script id="schema:show" type="application/ld\+json">.*?</script>' /tmp/$PODCAST_NAME.html 
# Extract JSON data between <script id="schema:show" type="application/ld+json"> and </script>
json_package="$(sed -n '/<script id=schema:show type="application\/ld+json">/,/<\/script>/p' /tmp/$PODCAST_NAME.html | sed '1d;$d')"

# format the JSON data
#echo "$json_package" | jq

# print the "name" and "url" for each "@type": "AudioObject"
#echo "$json_package" | jq '.itemListElement[] | select(.item["@type"] == "AudioObject") | .item.name, .item.url'
# Extract and iterate through all {name, url} pairs

CURRENT_DIR=$(pwd)
temp_dir=$(mktemp -d)

cd $temp_dir

jq -c '.workExample[] | select(."@type" == "AudioObject") | {name, url}' <<< "$json_package" | while IFS= read -r item; do
    name=$(jq -r '.name' <<< "$item")
    # replace all non-alphanumeric characters with underscores in name
    name=$(echo "$name" | sed 's/[^a-zA-Z0-9]/_/g')
    url=$(jq -r '.url' <<< "$item")
    
    # Call your function here with $name and $url
    echo "Arg:"  "$name" "$url"
    yt-dlp  "$url" -o "$name.%(ext)s"
done

cd $CURRENT_DIR
echo "Look in $temp_dir for the downloaded files"

exit 0
# | \
# sed 's/<script id="schema:show" type="application\/ld\+json">//g' | \
# sed 's/<\/script>//g'

#wget -qO- "$1" | grep -oP "https://podcasts.apple.com/us/podcast/[^\"/]+/$PODCAST_ID" > "$TMP"
# remove any duplicate lines in $TMP

echo "Before parsing the feed, the file $TMP contains:"

# find all the lines in $TMP that DON"T end in $PODCAST_ID and DO contain a question mark
# and write them to $TMP.tmp
#grep -v "$PODCAST_ID" "$TMP" | grep "?" > "$TMP".tmp
grep "?" "$TMP"  > "$TMP".tmp

#cat $TMP.tmp

exit 0

cat "$TMP" | sort -Ru | grep -v "$PODCAST_NAME" > "$TMP".tmp
mv "$TMP".tmp "$TMP"
yt-dlp -a $TMP


