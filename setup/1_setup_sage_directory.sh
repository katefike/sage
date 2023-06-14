#!/usr/bin/env bash

# Make the project root pwd
__dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd $__dir/..

echo "Copying .env File..."

if [ ! -f .env ]; then
    cp .env-example .env
fi

echo "Go to Step 3 in the README: Define the following environment variables in the .env file:"