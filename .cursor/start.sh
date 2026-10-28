#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/.."

if [[ ! -f .venv/bin/activate ]]; then
  echo "Missing .venv; run install first." >&2
  exit 1
fi

# shellcheck source=/dev/null
source .venv/bin/activate
exec python app.py
