#!/usr/bin/env sh
SCRIPT_DIR="$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)"
cd "$SCRIPT_DIR/.."
if [ -x "./portable/python/bin/python3" ]; then
  ./portable/python/bin/python3 -m app.main --mode cli
else
  python3 -m app.main --mode cli
fi
