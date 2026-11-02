#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd -- "$(dirname -- "$0")" && pwd -P)"
if [[ ! -r /etc/os-release ]]; then echo 'Cannot identify Linux distribution; run this installer on Ubuntu or a compatible Linux.' >&2; exit 1; fi
. /etc/os-release
[[ ${ID:-} == ubuntu || ${ID_LIKE:-} == *debian* ]] || { echo "Unsupported distribution: ${PRETTY_NAME:-unknown}. Ubuntu/Debian required for automatic package installation." >&2; exit 1; }
missing=()
for c in bash df du find ls awk sed grep date tar gzip stat sort tail hostname; do command -v "$c" >/dev/null || missing+=("$c"); done
if ((${#missing[@]})); then
  echo "Missing utilities: ${missing[*]}"
  echo 'Install base tools: sudo apt update && sudo apt install -y coreutils findutils gawk sed grep tar gzip cron'
fi
mkdir -p "$ROOT"/{data,logs,reports,backup,screenshots,tests}
touch "$ROOT/logs/storage_monitor.log" "$ROOT/logs/administrator_alerts.log"
[[ -s "$ROOT/data/storage_history.csv" ]] || printf 'timestamp,filesystem,mountpoint,total_bytes,used_bytes,available_bytes,usage_percent,inodes_total,inodes_used,inodes_free,inode_percent\n' > "$ROOT/data/storage_history.csv"
chmod 750 "$ROOT" "$ROOT/bin" "$ROOT/bin/lib" "$ROOT/tests" 2>/dev/null || true
find "$ROOT/bin" -type f -name '*.sh' -exec chmod 750 {} +
chmod 750 "$ROOT/install.sh"
chmod 640 "$ROOT/config/monitor.conf" "$ROOT/data/storage_history.csv" "$ROOT/logs/"*.log 2>/dev/null || true
echo "Project initialized at $ROOT"
echo 'Run: ./bin/run_all.sh'
echo 'Optional cron setup: ./bin/install_cron.sh'
