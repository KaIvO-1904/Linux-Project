#!/usr/bin/env bash
set -Eeuo pipefail
source "$(dirname -- "$0")/lib/common.sh"
load_config
init_history
stamp=$(date '+%Y%m%d_%H%M%S')
out="${PROJECT_ROOT}/${REPORT_DIR}/storage_report_${stamp}.txt"
{
  printf 'LINUX STORAGE MONITORING SYSTEM\nGenerated: %s\nHost: %s\n\n' "$(date '+%Y-%m-%d %H:%M:%S %z')" "$(hostname)"
  printf '%s\n' 'DISK USAGE (df -hP)' '-------------------'; df -hP
  printf '\n%s\n' 'INODE USAGE (df -iP)' '--------------------'; df -iP
  printf '\n%s\n' 'LARGEST DIRECTORIES (top-level /, best effort)' '-----------------------------------------------'
  du -x -h --max-depth=1 / 2>/dev/null | sort -h | tail -n "$REPORT_TOP_N" || true
  printf '\n%s\n' 'RECENT ALERTS' '-------------'; tail -n 50 "${PROJECT_ROOT}/${ALERT_LOG}" 2>/dev/null || true
  printf '\n%s\n' 'LATEST STORAGE HISTORY' '----------------------'; tail -n 20 "${PROJECT_ROOT}/${HISTORY_CSV}"
} > "$out"
chmod 640 "$out"
printf 'Report created: %s\n' "$out"
log INFO "Report generated: ${out#${PROJECT_ROOT}/}"
