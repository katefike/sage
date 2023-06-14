#!/usr/bin/env bash

# Make the project root pwd
__dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd $__dir/..

echo "Creating and activating Python virtrual environment (.venv) ..."

if [ ! -d .venv ]; then
    python3 -m venv .venv
fi

source .venv/bin/activate

echo "Installing Python Packages from requirements.txt in the .venv ..."

pip install -r requirements.txt

echo "Copying .env File..."

if [ ! -f .env ]; then
    cp .env-example .env
fi

echo "Copying .env File..."