#!/usr/bin/env bash
set -Eeuo pipefail
source "$(dirname -- "$0")/lib/common.sh"
load_config
printf '%-28s %14s %14s %14s %8s\n' FILESYSTEM INODES_TOTAL INODES_USED INODES_FREE IUSE%
while IFS= read -r line; do
  read -r fs total used avail pct mount <<< "$line"
  [[ $fs == Filesystem ]] && continue
  pct=${pct%%%}; [[ $pct =~ ^[0-9]+$ ]] || continue
  read -r fstype < <(stat -f -c %T -- "$mount" 2>/dev/null || printf 'unknown\n')
  excluded_fs "$fstype" && continue
  printf '%-28s %14s %14s %14s %7s%%  %s\n' "$fs" "$total" "$used" "$avail" "$pct" "$mount"
  check_threshold inode "$mount" "$pct" "$INODE_WARNING_THRESHOLD" "$INODE_CRITICAL_THRESHOLD"
done < <(df -P -i -- 2>/dev/null || df -P -i)
log INFO 'Inode usage scan completed.'
