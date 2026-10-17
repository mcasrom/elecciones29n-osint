#!/usr/bin/env bash
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
LOCAL="$REPO_DIR/web/"
REMOTE="deploy@178.105.80.193:/var/www/elecciones29n/"

if [ ! -d "$LOCAL" ]; then
  mkdir -p "$LOCAL"
fi

rsync -az --delete --info=stats --exclude=".DS_Store" "$LOCAL/" "$REMOTE/"
