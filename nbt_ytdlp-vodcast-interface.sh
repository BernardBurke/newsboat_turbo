if [[ "$1" == "" ]]; then
	echo "Please provide a URL"
	exit 1
fi

PODPATH=/media/Vodcasts

# write the current time and $1 into >> $HOME/yix_data.log
echo "$(date) $1" >> $HOME/yix_data.log



VIDEO_JSON=$(yt-dlp -j "$1")
uploader=$(echo "$VIDEO_JSON" | jq -r '.uploader')
# echo "Uploader: $uploader"
# uploader=$(echo "$uploader" | sed -e 's/[ &[:punct:]]/_/g' -e 's/[^[:alnum:]_]//g')

uploader=$(echo "$uploader" | sed 's/[^[:alnum:] ]//g')
# remove any leading or trailing spaces
uploader=$(echo "$uploader" | sed 's/^[ \t]*//;s/[ \t]*$//')
echo "Uploader: $uploader"

title=$(echo "$VIDEO_JSON" | jq -r '.title')
title=$(echo "$title" | sed 's/[^[:alnum:] ]//g')
title=$(echo "$title" | sed 's/^[ \t]*//;s/[ \t]*$//')
echo "Title: $title"
ext=$(echo "$VIDEO_JSON" | jq -r '.ext')
description=$(echo "$VIDEO_JSON" | jq -r '.description')
echo "Description: $description"
thumbnail=$(echo "$VIDEO_JSON" | jq -r '.thumbnail')
echo "Thumbnail: $thumbnail"


# if [[ $uploader == "" ]]; then
# 	echo "Uploader not found in json - using the default uploader string"
# 	PODTEMPSTRING="$PODPATH/%(uploader)s/%(title)s.%(ext)s"
# else
# 	# replace any spaces in $uploader with underscores
# 	uploader=$(echo "$uploader" | sed 's/ /_/g')
# 	PODTEMPSTRING="$PODPATH/$uploader/%(title)s.%(ext)s"
# fi

OUTPUT_FILENAME="$PODPATH/$uploader/$title.mp4"
# if the PODPATH/$uploader directory does not exist, create it
if [ ! -d "$PODPATH/$uploader" ]; then
	mkdir -p "$PODPATH/$uploader"
fi
PODTEMPSTRING="/tmp/$uploader/$title.$ext"

echo "Downloading smallest video to $PODTEMPSTRING"
if yt-dlp -S '+size,+br' "$1" -o "$PODTEMPSTRING"; then
	echo "Download complete"
else
	echo "Download failed"
	exit 1
fi

echo "Updating metadata"

ffmpeg -i "$PODTEMPSTRING"  -c copy -metadata ThumbnailURL=$thumbnail -metadata title="$title" -metadata description="$description" -metadata artist="$uploader" -metadata album_artist="$uploader" -metadata album="$uploader" -metadata genre="Podcast" -metadata year="$(date +%Y)" -metadata artwork="$thumbnail" "$OUTPUT_FILENAME"

#mv "$PODTEMPSTRING.tmp" "$PODTEMPSTRING" -v

#detox -v "$PODPATH/$uploader/"

# log the $1 and $PODTEMPSTRING to a file in $HOME called yix_data.log
#echo "$1" "$PODTEMPSTRING" >> $HOME/yix_data.log



