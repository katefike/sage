#!/bin/bash

# Make the project root pwd and export the current working directory
__dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd $__dir/../..
PROJECT_ROOT_PATH="$PWD"
export PROJECT_ROOT_PATH

set -o nounset -o pipefail -o errexit

# Load all variables from .env and export them all for Ansible to read
set -o allexport
source ".env"
set +o allexport

# Run Ansible Playbook for creating an ephemeral DO Droplet server
cd server/
exec ansible-playbook -i ansible/inventory_ephem.yml -i ansible/imported_playbooks/droplet_hosts ansible/imported_playbooks/create_droplet_ephem.yml --ask-become-pass