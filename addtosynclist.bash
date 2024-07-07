#!/bin/bash

# Define variables
CSV_FILE="/subaligner-bazarr/unsynced.csv"

# Get command line arguments
REFERENCE_FILE="$1"
SUB_FILE="$2"
SUB_CODE2="$3"
SUB_CODE3="$4"
SUB_ID="$5"
PROVIDER="$6"
SERIES_ID="$7"
EPISODE_ID="$8"

# Main logic
timestamp=$(date '+%Y-%m-%d %H:%M:%S')

# Check if file exists and create with headers if not
if [ ! -f "$CSV_FILE" ]; then
    echo "timestamp,episode,subtitles,subtitle_language_code2,subtitle_language_code3,subtitle_id,provider,series_id,episode_id" > "$CSV_FILE"
fi

# Prepare the data, properly escaping commas and quotes
data=("$timestamp" "$REFERENCE_FILE" "$SUB_FILE" "$SUB_CODE2" "$SUB_CODE3" "$SUB_ID" "$PROVIDER" "$SERIES_ID" "$EPISODE_ID")
csv_line=""
for field in "${data[@]}"; do
    if [[ $field == *","* || $field == *"\""* ]]; then
        field="\"${field//\"/\"\"}\""
    fi
    csv_line+="${csv_line:+,}$field"
done

# Append data to CSV file
if echo "$csv_line" >> "$CSV_FILE"; then
    echo "Successfully added \"$SUB_CODE2\"-subtitle to list!"
    sleep 0.1
else
    echo "Something went wrong, couldn't write to CSV-file..."
fi