#!/usr/bin/env bash

# This script is only run in production

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

# Convert $DOMAIN string to lowercase using two commas
certbot_cert=/etc/letsencrypt/live/prod.${DOMAIN,,}/fullchain.pem
certbot_key=/etc/letsencrypt/live/prod.${DOMAIN,,}/privkey.pem

# Check if a cert and key exist or not
if ! [[ -f ${certbot_cert} && -f ${certbot_key} ]]; then
    echo "Cert file not found at: ${certbot_cert}. Private key not found at: ${certbot_key}"

    # If they don't exist, create new certs (in a dry run during development)
    echo "Genererating TLS certs..."
    docker run --rm \
    --name certbot \
    -p 80:80 \
    -v "/etc/letsencrypt:/etc/letsencrypt" \
    -v "/var/lib/letsencrypt:/var/lib/letsencrypt" \
    certbot/certbot certonly --standalone --dry-run --agree-tos --non-interactive -m ${FORWARDING_EMAIL} -d prod.${DOMAIN}

    if ! [[ -f ${certbot_cert} && -f ${certbot_key} ]]; then
        echo "CRITICAL ERROR: Failed to generate TLS certs."
        exit
    fi

else
    # If they exist, check if they're expired
    current_date=$(date)

    # Get the expiration date of the certificate
    cert_expiration_date=$(openssl x509 -enddate -noout -in ${certbot_cert} | cut -d= -f2)
    # Get the earliest date the certificate can be renewed (30 days before the expiration)
    cert_renewal_date=$(date -d "${cert_expiration_date} -30 days")
    echo "Expiration date: ${cert_expiration_date}"
    echo "Renewal date: ${cert_renewal_date}"

    # Check if the certificate has passed the renewal date
    if [[ "${current_date}" > "${cert_renewal_date}" ]]; then
        exit
    fi

    echo "The TLS cert is expires on ${cert_expiration_date}. Renewing in a dry-run..."
    docker run --rm \
        --name certbot \
        -p 80:80 \
        -v "/etc/letsencrypt:/etc/letsencrypt" \
        -v "/var/lib/letsencrypt:/var/lib/letsencrypt" \
        certbot/certbot renew --dry-run
        # TODO: Use --deploy-hook to load certs and restart mailserver container

    # Get the new expiration date of the certificate
    new_cert_expiration_date=$(openssl x509 -enddate -noout -in ${certbot_cert} | cut -d= -f2)
    # Check if the renewal was successful
    if [[ "${new_cert_expiration_date}" == "${cert_expiration_date}" ]]; then
        echo "CRITICAL ERROR: Failed to renew TLS certs."
        exit
    fi
fi

echo "Checking if a TLS connection can be made from the server..."
if ! openssl s_client -connect prod.${DOMAIN}:587 -starttls smtp | grep -q 'CONNECTED'; then
    echo "CRITICAL ERROR: Failed to connect using TLS."
    exit
fi
echo "Successfully made a TLS connection."

echo "Copying TLS certs to sage-mailserver Docker container..."
docker cp ${certbot_cert} sage-mailserver:${certbot_cert}
docker cp ${certbot_key} sage-mailserver:${certbot_key}

echo "Restarting the sage-mailserver Docker container..."
docker restart sage-mailserver

echo "Checking if a TLS connection can be made from inside the sage-mailserver Docker container..."
if ! [[ docker exec sage-mailserver openssl s_client -connect prod.${DOMAIN}:993 -starttls smtp | grep -q 'CONNECTED' ]]; then
    echo "CRITICAL ERROR: Failed to connect using TLS."
    exit
fi
echo "Successfully made a TLS connection."