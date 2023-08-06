#!/usr/bin/env bash

# Make the project root pwd
__dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd $__dir/..

echo "Creating the Digital Droplet hosts file..."
if [ ! -f server/ansible/imported_playbooks/droplet_hosts ]; then
    cp server/ansible/imported_playbooks/droplet_hosts_example \
    server/ansible/imported_playbooks/droplet_hosts
fi

echo "Copying .env file..."

if [ ! -f .env ]; then
    cp .env-example .env
fi

echo "Go to Step 3 in the README: Define the following environment variables in the .env file:"