if [[ "$1" == "" ]]; then
	echo "Please provide a URL"
	exit 1
fi

PODPATH=~/Poddle

# write the current time and $1 into >> $HOME/yix_data.log
echo "$(date) $1" >> $HOME/yix_data.log

get_uploader() {

	youtube_url="$1"

	# Get video info in JSON format
	video_info=$(yt-dlp -j "$youtube_url")

	# Extract and print uploader
	uploader=$(echo "$video_info" | jq -r '.uploader')

	uploader=$(echo "$uploader" | sed -e 's/[ &[:punct:]]/_/g' -e 's/[^[:alnum:]_]//g') 

	if [[ -z "$uploader" ]]; then
		echo ""	
	else
		echo "$uploader"
	fi
}


# Get uploader
uploader=$(get_uploader "$1")

if [[ $uploader == "" ]]; then
	echo "Uploader not found in json - using the default uploader string"
	PODOUTUPTSTRING="$PODPATH/%(uploader)s/%(title)s.%(ext)s"
else
	# replace any spaces in $uploader with underscores
	uploader=$(echo "$uploader" | sed 's/ /_/g')
	PODOUTUPTSTRING="$PODPATH/$uploader/%(title)s.%(ext)s"
fi


if yt-dlp -f 140 "$1" -o "$PODOUTUPTSTRING"; then
	echo "140 download complete"
	break
else
	echo "140 format not available - trying 139"
	yt-dlp -f 139 "$1" -o "$PODOUTUPTSTRING"
fi


detox -v "$PODPATH/$uploader/"

# log the $1 and $PODOUTUPTSTRING to a file in $HOME called yix_data.log
echo "$1" "$PODOUTUPTSTRING" >> $HOME/yix_data.log



