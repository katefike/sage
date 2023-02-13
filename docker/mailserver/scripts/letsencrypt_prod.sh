#!/usr/bin/env bash

# Get TLS certs
echo "Generating TLS certs..."
certbot certonly --dry-run --non-interactive --standalone --agree-tos -m ${FORWARDING_EMAIL} -d ${HOST}.${DOMAIN}
