#!/bin/bash

# Function to summarize grep -H output
# Input: A single string argument in the format "filepath:line_of_text"
# Output: A summarized string "processed_filename:processed_text"
summarize_grep_output() {
  # Ensure an argument is provided
  if [[ -z "$1" ]]; then
    echo "Usage: summarize_grep_output \"filepath:line_of_text\"" >&2
    return 1
  fi

  local input_line="$1"
  local filepath
  local line
  local filename
  local processed_filename
  local processed_line

  # Separate filepath and line using the first colon as delimiter
  # %%:* removes the longest suffix starting with : (greedy from the right)
  filepath="${input_line%%:*}"
  # #*: removes the shortest prefix ending with : (non-greedy from the left)
  line="${input_line#*:}"

  # --- Process Filename ---
  # 1. Get just the filename from the path
  filename=$(basename "$filepath")
  # 2. Remove all non-alphabetic characters (keeps spaces temporarily)
  #    tr -cd '[:alpha:] ' deletes all characters NOT in the set {alphabetic, space}
  # 3. Replace spaces with underscores
  #    tr ' ' '_' replaces spaces with underscores
  processed_filename=$(echo "$filename" | tr -cd '[:alpha:] ' | tr ' ' '_')

  # --- Process Line ---
  # 1. Remove all non-alphabetic characters.
  #    Based on your description "do the same remove alpha and underscores",
  #    interpreted as applying the "remove non-alphabetic" rule like the filename,
  #    but *without* the space-to-underscore conversion. If you truly meant
  #    "remove *alphabetic* characters and underscores", change the command below.
  #    tr -cd '[:alpha:]' deletes all characters NOT in the set {alphabetic}
  # 2. Truncate the result to a maximum of 200 characters (bytes)
  #    head -c 200 takes the first 200 bytes
  processed_line=$(echo "$line" | tr -cd '[:alpha:]' | head -c 200)

  # Output the result in the desired format
  echo "${processed_filename}:${processed_line}"
}

# --- Example Usage ---

# Example input string (simulate grep -H output)
# grep_output="/path/to/My Report File v1.2 (draft).txt:This is line 1, containing important details & numbers like 12345 and maybe some very long text that needs to be truncated properly because it exceeds the two hundred character limit significantly."

# Call the function with the example input
# summarize_grep_output "$grep_output"

# --- How to Use ---
# 1. Save the function definition (the part between 'summarize_grep_output() {' and '}')
#    to your ~/.bashrc or ~/.bash_profile file.
# 2. Source the file (e.g., `source ~/.bashrc`) or open a new terminal window.
# 3. Pipe your grep output to a loop or use it directly:
#    grep -H "some pattern" /path/to/files* | while IFS= read -r line; do summarize_grep_output "$line"; done
#    # Or for a single line:
#    my_line=$(grep -H "pattern" some_file.txt | head -n 1)
#    summarize_grep_output "$my_line"