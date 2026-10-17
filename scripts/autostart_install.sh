#!/usr/bin/env bash
set -euo pipefail
mkdir -p ~/.config/autostart
cp "$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/elecciones29n-watchdog.desktop" ~/.config/autostart/
echo "autostart instalado"
