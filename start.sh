#!/bin/bash

HOST_SCRIPTS_DIR="/subaligner-bazarr"
CONTAINER_SCRIPTS_DIR="/opt/subaligner-bazarr"
FILE=("addtosynclist.bash")

# Copy scripts to host directory
if [ -d "$HOST_SCRIPTS_DIR" ]; then
    if [ -f "$CONTAINER_SCRIPTS_DIR/$FILE" ]; then
        cp -R "$CONTAINER_SCRIPTS_DIR/$FILE" "$HOST_SCRIPTS_DIR/"
        chmod +x "$HOST_SCRIPTS_DIR/$FILE"
    else
        echo "Warning: $FILE not found in $CONTAINER_SCRIPTS_DIR"
    fi

    if [ -f "$HOST_SCRIPTS_DIR/$FILE" ]; then
        echo "Scripts are in place!"
    else
        echo "ERROR: \"$HOST_SCRIPTS_DIR/$FILE\" not found"
    fi

    /usr/bin/python3 -u $CONTAINER_SCRIPTS_DIR/main.py | tee mainlog
else
    echo "ERROR: Make sure the container has the container path \"$HOST_SCRIPTS_DIR\" allocated..."
fi