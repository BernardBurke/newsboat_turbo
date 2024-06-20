if [[ $1 == "" ]]; then
	echo "Please provide a URL"
	exit 1
fi

PODPATH=~/Poddle

yt-dlp -f 139 $1 -o "$PODPATH/%(uploader)s/%(title)s.%(ext)s"
