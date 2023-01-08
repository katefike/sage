#!/usr/bin/env bash

# Make the project root pwd
__dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd $__dir/..

echo "1. Create and/or activate Python virtrual environment (.venv) ..."

if [ ! -d .venv ]; then
    python3 -m venv .venv
fi

source .venv/bin/activate

echo "2. Install Python Packages from requirements.txt in the .venv ..."

pip install -r requirements.txt

echo "3. Copying .env File..."

if [ ! -f .env ]; then
    cp .env-example .env
fi