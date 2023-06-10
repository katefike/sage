#!/bin/bash

# Make the project root pwd
__dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd $__dir/..

set -o nounset -o pipefail -o errexit

# Load all variables from .env and export them all for Ansible to read
set -o allexport
source ".env"
set +o allexport

# Run Ansible Playbook for configuration as the regular user with sudo privileges on the DO Droplet server. The username is defined in the .env.
cd server/
exec ansible-playbook -i ansible/inventory_ephem.yml -i ansible/imported_playbooks/droplet_hosts ansible/imported_playbooks/configure_user_droplet_ephem.yml