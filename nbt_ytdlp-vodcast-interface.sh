if [[ "$1" == "" ]]; then
	echo "Please provide a URL"
	exit 1
fi

if [[ "$PODPATH" != "" ]]; then
	echo "PODPATH set externally to $PODPATH"
else
	PODPATH=/media/Vodcasts
fi

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
echo "File extension $ext"
description=$(echo "$VIDEO_JSON" | jq -r '.description')
# add a line break the current description and add the URL via $1 to description
description="$description   -- original_url: $1"
echo "Description: $description"
thumbnail=$(echo "$VIDEO_JSON" | jq -r '.thumbnail')
echo "Thumbnail: $thumbnail"

json_filename="$(echo "$VIDEO_JSON" | jq -r '.filename')"
echo "Filename from json" 
# if [[ $uploader == "" ]]; then
# 	echo "Uploader not found in json - using the default uploader string"
# 	PODTEMPSTRING="$PODPATH/%(uploader)s/%(title)s.%(ext)s"
# else
# 	# replace any spaces in $uploader with underscores
# 	uploader=$(echo "$uploader" | sed 's/ /_/g')
# 	PODTEMPSTRING="$PODPATH/$uploader/%(title)s.%(ext)s"
# fi

#OUTPUT_FILENAME="$PODPATH/$uploader/$title.$ext"

OUTPUT_FILENAME="$PODPATH/$uploader/$title.m4a"
# if the PODPATH/$uploader directory does not exist, create it
if [ ! -d "$PODPATH/$uploader" ]; then
	mkdir -p "$PODPATH/$uploader"
fi
# PODTEMPSTRING="/tmp/$uploader/$title.$ext"
PODTEMPSTRING="/tmp/$uploader/$title.m4a"

echo "Downloading smallest video to $PODTEMPSTRING"
if yt-dlp -f 'bestaudio[ext=m4a]' "$1" -o "$PODTEMPSTRING"; then
	echo "Download complete"
else
	echo "Download failed - url saved to $HOME/yix__error_data.log"
	echo "$1" >> $HOME/yix__error_data.log
	read -p "Press enter to try again"
	if yt-dlp -f 'bestaudio[ext=m4a]' "$1" -o "$PODTEMPSTRING"; then
		echo "Download completed on second try"
	else
		echo "Download failed again"
		echo "$1" >> $HOME/yix__error_data.log
	fi
	exit 1
fi

echo "Updating metadata"

if [[ ! -f "$PODTEMPSTRING" ]]; then
	echo "File not found. Exiting"
	exit 1
fi
	# echo "Looks like outputfile changed. Trying to add .mkv for the sake of ffmpeg"
	# exit 1
	# PODTEMPSTRING="${PODTEMPSTRING}.mkv"
	# OUTPUT_FILENAME="${title}.mp4"
	#fi


ffmpeg -i "$PODTEMPSTRING"  -c copy  -metadata title="$title" -metadata description="$description" -metadata artist="$uploader" -metadata album_artist="$uploader" -metadata album="$uploader" -metadata genre="Podcast" -metadata year="$(date +%Y)" -metadata artwork="$thumbnail" "$OUTPUT_FILENAME"

#mv "$PODTEMPSTRING.tmp" "$PODTEMPSTRING" -v

#detox -v "$PODPATH/$uploader/"

# log the $1 and $PODTEMPSTRING to a file in $HOME called yix_data.log
#echo "$1" "$PODTEMPSTRING" >> $HOME/yix_data.log



