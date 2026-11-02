#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd -- "$(dirname -- "$0")/.." && pwd -P)"
"${ROOT}/bin/disk_monitor.sh"
"${ROOT}/bin/inode_monitor.sh"
"${ROOT}/bin/storage_growth.sh"
"${ROOT}/bin/generate_report.sh"
printf '\nRun completed. Logs: %s/logs | Reports: %s/reports\n' "$ROOT" "$ROOT"
