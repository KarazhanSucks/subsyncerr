#!/bin/bash

CRON_SCHEDULE=${CRON_SCHEDULE:-"30 * * * *"}
HOST_SCRIPTS_DIR="/subaligner-bazarr"
CONTAINER_SCRIPTS_DIR="/opt/subaligner-bazarr"
FILES_TO_COPY=("addtosynclist.bash" "main.py")

# Copy scripts to host directory
if [ -d "$HOST_SCRIPTS_DIR" ]; then
    for file in "${FILES_TO_COPY[@]}"; do
        if [ -f "$CONTAINER_SCRIPTS_DIR/$file" ]; then
            cp -R "$CONTAINER_SCRIPTS_DIR/$file" "$HOST_SCRIPTS_DIR/"
        else
            echo "Warning: $file not found in $CONTAINER_SCRIPTS_DIR"
        fi
    done
    for script in "${FILES_TO_COPY[@]}"; do
    script_name=$(basename "$script")
    if [ -f "$HOST_SCRIPTS_DIR/$script_name" ]; then
        echo "$script_name: Found"
    else
        echo "ERROR: \"$script_name\" not found"
    fi
    done
else
    echo "ERROR: Make sure the container has the container path \"$HOST_SCRIPTS_DIR\" allocated..."
fi

# Set up cron job
echo "$CRON_SCHEDULE python3 $HOST_SCRIPTS_DIR/main.py >> /var/log/cron.log 2>&1" > /etc/cron.d/my-cron-job
chmod 0644 /etc/cron.d/my-cron-job
crontab /etc/cron.d/my-cron-job

# Start cron
cron

tail -f /var/log/cron.log &

echo "Cron-schedule in use: $CRON_SCHEDULE"

# Keep container running and output status
while true; do
    echo "$(date): Container is running!"
    sleep 7200
done