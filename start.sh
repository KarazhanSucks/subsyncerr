#!/bin/bash

CRON_SCHEDULE=${CRON_SCHEDULE:-"30 * * * *"}
HOST_SCRIPTS_DIR="/subaligner-bazarr"
CONTAINER_SCRIPTS_DIR="/opt/subaligner-bazarr"

# Copy scripts to host directory
cp -R $CONTAINER_SCRIPTS_DIR/* $HOST_SCRIPTS_DIR/

# Check if scripts are present in host directory
echo "Checking scripts in $HOST_SCRIPTS_DIR:"
for script in $CONTAINER_SCRIPTS_DIR/*; do
    script_name=$(basename $script)
    if [ "$script_name" != "start.sh" ]; then
        if [ -f "$HOST_SCRIPTS_DIR/$script_name" ]; then
            echo "  $script_name: Found"
        else
            echo "  $script_name: Not found"
        fi
    fi
done

# Set up cron job
echo "$CRON_SCHEDULE /usr/local/bin/python $HOST_SCRIPTS_DIR/main.py >> /var/log/cron.log 2>&1" > /etc/cron.d/my-cron-job
chmod 0644 /etc/cron.d/my-cron-job
crontab /etc/cron.d/my-cron-job

# Start cron
cron

# Keep container running and output status
while true; do
    echo "$(date): Container is running!"
    sleep 7200