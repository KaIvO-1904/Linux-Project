#!/usr/bin/env bash
set -Eeuo pipefail
source "$(dirname -- "$0")/lib/common.sh"
load_config
printf '%-28s %12s %12s %12s %8s\n' FILESYSTEM TOTAL USED AVAILABLE USE%
while IFS= read -r line; do
  read -r fs total used avail pct mount <<< "$line"
  [[ $fs == Filesystem ]] && continue
  pct=${pct%%%}; [[ $pct =~ ^[0-9]+$ ]] || continue
  read -r fstype < <(stat -f -c %T -- "$mount" 2>/dev/null || printf 'unknown\n')
  excluded_fs "$fstype" && continue
  printf '%-28s %12s %12s %12s %7s%%  %s\n' "$fs" "$total" "$used" "$avail" "$pct" "$mount"
  check_threshold disk "$mount" "$pct" "$WARNING_THRESHOLD" "$CRITICAL_THRESHOLD"
done < <(df -P -B1 -- 2>/dev/null || df -P -B1)
log INFO 'Disk usage scan completed.'
