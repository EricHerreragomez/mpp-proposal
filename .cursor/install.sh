#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

if ! python3 -m venv /tmp/_venv_probe 2>/dev/null; then
  sudo DEBIAN_FRONTEND=noninteractive apt-get update -qq
  sudo DEBIAN_FRONTEND=noninteractive apt-get install -y -qq python3-venv
fi
rm -rf /tmp/_venv_probe

if [[ ! -d .venv ]]; then
  python3 -m venv .venv
fi

.venv/bin/pip install -r requirements.txt
