#!/usr/bin/env bash
set -euo pipefail
REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
UNIT_DIR="$HOME/.config/systemd/user"
STATE_DIR="$HOME/.local/state/elecciones29n"
APP_DIR="$HOME/.local/share/applications"
mkdir -p "$UNIT_DIR" "$STATE_DIR" "$APP_DIR"
cp "$REPO_DIR/scripts/systemd/elecciones29n-attention.service" "$UNIT_DIR/"
cp "$REPO_DIR/scripts/systemd/elecciones29n-attention.timer" "$UNIT_DIR/"
printf '%s\n' \
  '[Desktop Entry]' \
  'Type=Application' \
  'Name=29N - Pendientes' \
  'Comment=Panel local de avisos de Elecciones 29N' \
  "Exec=xdg-open $HOME/.config/elecciones29n/needs.html" \
  'Icon=dialog-information' \
  'Terminal=false' \
  'Categories=Utility;' \
  > "$APP_DIR/elecciones29n-needs.desktop"
chmod +x "$REPO_DIR/scripts/needs.py"
systemctl --user daemon-reload
systemctl --user enable --now elecciones29n-attention.timer
command -v update-desktop-database >/dev/null && update-desktop-database "$APP_DIR" >/dev/null 2>&1 || true
systemctl --user list-timers elecciones29n-attention.timer
