#!/usr/bin/env bash

# TLS CERTS: Only run in production
# if [[ -f "/letsencrypt.sh" ]]; then
#   bash /letsencrypt.sh
#   if [[ -f "${CRT_FILE}" && -f "${KEY_FILE}" ]]; then
#     if ![[ openssl s_client -connect ${HOST}.${DOMAIN}:993 -starttls smtp | grep -q 'CONNECTED']]; then
#       echo 'CRITICAL ERROR: Failed to connect using TLS.'
#     fi
#   else
#     echo 'CRITICAL ERROR: Failed to find TLS cert files.'
#   fi
#   ufw deny 80
# fi

# Make the project root pwd and export the current working directory
__dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd $__dir/../..
PROJECT_ROOT_PATH="$PWD"
export PROJECT_ROOT_PATH

set -o nounset -o pipefail -o errexit

# Load all variables from .env and export them all
set -o allexport
source ".env"
set +o allexport

echo "Attempting to generate TLS certs in a dry run..."
certbot certonly --dry-run --non-interactive --standalone --agree-tos -m ${FORWARDING_EMAIL} -d ${HOST}.${DOMAIN}

# Check if dry run was successful

# Check if certs exist
# If no -> Check if certs are expired
# If yes -> Check if certs are expired