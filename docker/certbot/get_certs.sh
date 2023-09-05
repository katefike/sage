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
echo "VARS: ${FORWARDING_EMAIL} -d ${HOST}.${DOMAIN}"
# echo "Attempting to generate TLS certs in a dry run..."
# certbot certonly --dry-run --non-interactive --standalone --agree-tos -m ${FORWARDING_EMAIL} -d ${HOST}.${DOMAIN}