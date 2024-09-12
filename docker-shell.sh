#!/bin/bash

set -e
CSV_FILE="../secrets/s3bucket_programmatic_access_accessKeys.csv"

# Check if the file exists and is readable
if [ ! -r "$CSV_FILE" ]; then
    echo "Error: Cannot read $CSV_FILE. Check if it exists and has correct permissions."
    exit 1
fi

# Create the .env file
AWS_ACCESS_KEY_ID=$(awk -F ',' 'NR==2 {print $1}' "$CSV_FILE")
AWS_SECRET_ACCESS_KEY=$(awk -F ',' 'NR==2 {print $2}' "$CSV_FILE")

echo "AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID" > .env
echo "AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY" >> .env

# Source the .env file
source .env

# Create the network if we don't have it yet
docker network inspect data-labeling-network >/dev/null 2>&1 || docker network create data-labeling-network

# Build the image based on the Dockerfile
docker build -t data-label-cli -f Dockerfile .

# Run All Containers
docker-compose run --rm --service-ports data-label-cli