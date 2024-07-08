#!/bin/bash

HOST_SCRIPTS_DIR="/subaligner-bazarr"
CONTAINER_SCRIPTS_DIR="/opt/subaligner-bazarr"
FILE=("addtosynclist.bash")

# Copy scripts to host directory
if [ -d "$HOST_SCRIPTS_DIR" ]; then
    if [ -f "$CONTAINER_SCRIPTS_DIR/$file" ]; then
        cp -R "$CONTAINER_SCRIPTS_DIR/$file" "$HOST_SCRIPTS_DIR/"
    else
        echo "Warning: $file not found in $CONTAINER_SCRIPTS_DIR"
    fi

    script_name=$(basename "$script")
    if [ -f "$HOST_SCRIPTS_DIR/$script_name" ]; then
        echo "Scripts are in place!"
    else
        echo "ERROR: \"$script_name\" not found"
    fi

    echo "API-KEY: ${API_KEY}"
    echo "BAZARR_URL: ${BAZARR_URL}"
    echo "SUBCLEANER: ${SUBCLEANER}"
    echo "SLEEP: ${SLEEP}"

    /usr/bin/python3 $CONTAINER_SCRIPTS_DIR/main.py | mainlog

    # Keep container running and output status
    while true; do
        echo "$(date): Container is running!"
        echo ""
        sleep 7200
    done
else
    echo "ERROR: Make sure the container has the container path \"$HOST_SCRIPTS_DIR\" allocated..."
fi