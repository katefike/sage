#!/bin/bash

if [ -z "$ENVIRONMENT" ]; then
   echo "SCHEDULER_ENVIRONMENT not set, assuming Development"
   ENVIRONMENT="development"
fi

# Select the crontab file based on the environment
CRON_FILE="crontab.$ENVIRONMENT"

echo "Loading crontab file: $CRON_FILE"

# Load the crontab file
crontab $CRON_FILE

# Start cron
echo "Starting cron..."
crond -f