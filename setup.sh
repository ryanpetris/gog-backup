#!/bin/bash

set -e
set -o pipefail

cd "$(dirname "${BASH_SOURCE[0]}")"

if [ ! -d .venv ]; then
    python -m venv .venv
fi

source .venv/bin/activate
pip install -r requirements.txt
