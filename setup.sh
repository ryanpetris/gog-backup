#!/bin/bash

set -e
set -o pipefail

cd "$(dirname "${BASH_SOURCE[0]}")"

if [ ! -d .venv ]; then
    python -m venv .venv
fi

pip install -r requirements.txt
