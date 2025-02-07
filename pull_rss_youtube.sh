#!/bin/bash

# Function to extract rssUrl using grep and cut (for simple cases)
extract_rss_grep() {
  local html_source="$1"
  barney="$(curl -s  $1 | grep -Po  '(?<=href=")[^"]*' | grep  videos.xml)"
  echo $barney

}

rss_url="$(extract_rss_grep $1)"

# Output the rssUrl
if [[ -n "$rss_url" ]]; then  # Check if rss_url is not empty
  echo "$rss_url"
else
  echo "rssUrl not found."
fi
