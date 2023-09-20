#!/usr/bin/env bash

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

# Runs Ansible Playbook for configuring the ephemeral DO Droplet server.
cd ansible/
exec ansible-playbook -i imported_playbooks/droplet_hosts main_configure_ephem.yml --ask-become-pass