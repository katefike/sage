#!/bin/bash
set -o nounset -o pipefail -o errexit

# Load all variables from .env and export them all for Ansible to read
set -o allexport
cd ..
source ".env"
set +o allexport

# Run Ansible Playbook for creating an ephemeral DO Droplet server
cd ansible/
exec ansible-playbook -i inventory_production.yml create_droplet_production.yml --ask-become-pass