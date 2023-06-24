#!/usr/bin/env bash

echo "**WARNING: RUNNING THIS SCRIPT CAUSES DIGITAL OCEAN TO START CHARGING YOU FOR A SERVER ON A MONTHLY BASIS.**"
read -r -p "Are you sure? [y/N] " response
if ! [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]
then
    exit
fi

# Make the project root pwd
__dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd $__dir/../..
set -o nounset -o pipefail -o errexit

# Load all variables from .env and export them all for Ansible to read
set -o allexport
source ".env"
set +o allexport

# Runs Ansible Playbook for creating a ephemeral DO Droplet server. The server runs the application Sage.
cd server/ansible/
exec ansible-playbook -i inventory_ephem.yml -i imported_playbooks/droplet_hosts main_ephem.yml --ask-become-pass