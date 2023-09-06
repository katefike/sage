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

certbot_cert=/etc/letsencrypt/live/${HOST}.${DOMAIN}/fullchain.pem
certbot_key=/etc/letsencrypt/live/${HOST}.${DOMAIN}/privkey.pem

# Check if a cert and key exist or not
if ![[ -f ${certbot_cert} && -f ${certbot_key} ]]; then
    # If they don't exist, create new certs (in a dry run during development)
    echo 'Genererating TLS certs in a dry-run...'
    docker run --rm -it \
    --name certbot \
    -v "/etc/letsencrypt:/etc/letsencrypt" \
    -v "/var/lib/letsencrypt:/var/lib/letsencrypt" \
    certonly --agree-tos --dry-run --non-interactive -m ${FORWARDING_EMAIL} -d ${HOST}.${DOMAIN}

else
    # If they exist, check if they're expired
    current_date=$(date +%s)

    # Get the expiration date of the certificate
    raw_cert_expiration$(openssl x509 -enddate -noout -in ${certbot_cert} | cut -d= -f2)
    cert_expiration=$(date -d "${raw_cert_expiration}" +%s)

    # Check if the certificate has passed the expiration date
    if ![[ ${current_date} -gt ${cert_expiration} ]]; then
        exit
    fi

    echo 'The TLS cert is expired. Renewing...'
    docker run --rm -it \
        --name certbot \
        -v "/etc/letsencrypt:/etc/letsencrypt" \
        -v "/var/lib/letsencrypt:/var/lib/letsencrypt" \
        rewnew --agree-tos --dry-run --non-interactive -m ${FORWARDING_EMAIL} -d ${HOST}.${DOMAIN}

    if ![[ -f ${certbot_cert} && -f ${certbot_key} ]]; then
        echo 'CRITICAL ERROR: Failed to renew expired TLS certs.'
        exit
    fi
fi

if [[ -f ${certbot_cert} && -f ${certbot_key} ]]; then
    echo 'Checking if a TLS connection can be made from the server...'
    if ![[ openssl s_client -connect ${HOST}.${DOMAIN}:993 -starttls smtp | grep -q 'CONNECTED' ]]; then
        echo 'CRITICAL ERROR: Failed to connect using TLS.'
        exit
    fi
    echo 'Successfully made a TLS connection.'
fi

echo 'Copying TLS certs to sage-mailserver Docker container...'
docker cp ${certbot_cert} sage-mailserver:${certbot_cert}
docker cp ${certbot_key} sage-mailserver:${certbot_key}

echo 'Restarting the sage-mailserver Docker container...'
docker restart sage-mailserver

echo 'Checking if a TLS connection can be made from inside the sage-mailserver Docker container...'
if ![[ docker exec sage-mailserver openssl s_client -connect ${HOST}.${DOMAIN}:993 -starttls smtp | grep -q 'CONNECTED' ]]; then
    echo 'CRITICAL ERROR: Failed to connect using TLS.'
    exit
fi
echo 'Successfully made a TLS connection.'