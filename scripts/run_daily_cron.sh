#!/usr/bin/env bash
set -euo pipefail
cd /home/deploy/elecciones29n-osint
mkdir -p logs
exec ./scripts/run_daily_server.sh >> logs/run_daily.log 2>&1
