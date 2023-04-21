#!/bin/bash

# Make the project root pwd
__dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd $__dir/..

set -o nounset -o pipefail -o errexit

# Load all variables from .env and export them all for Ansible to read
set -o allexport
source ".env"
set +o allexport

# Run Ansible Playbook for creating an ephemeral DO Droplet server
cd server
exec ansible-playbook -i ansible/inventory_ephem.yml ansible/create_droplet_ephem.yml --ask-become-pass