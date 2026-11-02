#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd -- "$(dirname -- "$0")/.." && pwd -P)"
command -v crontab >/dev/null || { echo 'crontab is unavailable. Install cron on Ubuntu: sudo apt install cron'; exit 1; }
tmp=$(mktemp)
trap 'rm -f "$tmp"' EXIT
crontab -l 2>/dev/null | grep -v '# LINUX_STORAGE_MONITOR ' > "$tmp" || true
printf '*/5 * * * * %q/bin/monitor_cycle.sh >> %q/logs/cron.log 2>&1 # LINUX_STORAGE_MONITOR monitor\n' "$ROOT" "$ROOT" >> "$tmp"
printf '*/15 * * * * %q/bin/generate_report.sh >> %q/logs/cron.log 2>&1 # LINUX_STORAGE_MONITOR report\n' "$ROOT" "$ROOT" >> "$tmp"
crontab "$tmp"
echo 'Installed per-user cron entries:'
crontab -l | grep '# LINUX_STORAGE_MONITOR'
