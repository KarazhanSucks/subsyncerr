#!/bin/bash

if [ ! -x "$0" ]; then
    echo "ERROR: Script doesn't have execution permissions!"
    echo "Please run: chmod +x $0"
    exit 1
fi

CSV_FILE="/subsync-bazarr/unsynced.csv"

REFERENCE_FILE="$1"
SUB_FILE="$2"
SUB_CODE2="$3"
SUB_CODE3="$4"
EP_CODE3="$5"
SUB_ID="$6"
PROVIDER="$7"
SERIES_ID="$8"
EPISODE_ID="$9"

timestamp=$(date '+%Y-%m-%d %H:%M:%S')

if [ ! -f "$CSV_FILE" ]; then
    echo "timestamp,episode,subtitles,subtitle_language_code2,subtitle_language_code3,episode_language_code3,subtitle_id,provider,series_id,episode_id" > "$CSV_FILE"
    chmod 666 "$CSV_FILE"
fi

data=("$timestamp" "$REFERENCE_FILE" "$SUB_FILE" "$SUB_CODE2" "$SUB_CODE3" "$EP_CODE3" "$SUB_ID" "$PROVIDER" "$SERIES_ID" "$EPISODE_ID")
csv_line=""
for field in "${data[@]}"; do
    if [[ $field == *","* || $field == *"\""* ]]; then
        field="\"${field//\"/\"\"}\""
    fi
    csv_line+="${csv_line:+,}$field"
done

if echo "$csv_line" >> "$CSV_FILE"; then
    echo "Successfully added \"$SUB_CODE2\"-subtitle to list!"
    sleep 0.1
else
    echo "ERROR: Something went wrong, couldn't write to CSV-file..."
fi