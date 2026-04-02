#!/bin/sh
set -eu

exec python3 "$(dirname "$0")/llm_selection_transform.py" "$@"
