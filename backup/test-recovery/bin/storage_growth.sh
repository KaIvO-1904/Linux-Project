#!/usr/bin/env bash
set -Eeuo pipefail
source "$(dirname -- "$0")/lib/common.sh"
load_config
init_history
timestamp=$(date '+%Y-%m-%dT%H:%M:%S%z')
declare -A inode_map=()
while IFS= read -r line; do
  read -r fs it iu ifree ipct mount <<< "$line"
  [[ $fs == Filesystem ]] && continue
  ipct=${ipct%%%}; inode_map["$mount"]="$it,$iu,$ifree,$ipct"
done < <(df -P -i -- 2>/dev/null || df -P -i)
printf 'Storage snapshot at %s\n' "$timestamp"
while IFS= read -r line; do
  read -r fs total used avail pct mount <<< "$line"
  [[ $fs == Filesystem ]] && continue
  pct=${pct%%%}; [[ $pct =~ ^[0-9]+$ ]] || continue
  read -r fstype < <(stat -f -c %T -- "$mount" 2>/dev/null || printf 'unknown\n')
  excluded_fs "$fstype" && continue
  IFS=, read -r it iu ifree ipct <<< "${inode_map[$mount]:-0,0,0,0}"
  printf '%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n' "$timestamp" "${fs//,/ }" "${mount//,/ }" "$total" "$used" "$avail" "$pct" "$it" "$iu" "$ifree" "$ipct" >> "${PROJECT_ROOT}/${HISTORY_CSV}"
  previous=$(awk -F, -v m="$mount" -v now="$timestamp" '$3==m && $1!=now {p=$5} END {if (p != "") print p}' "${PROJECT_ROOT}/${HISTORY_CSV}")
  if [[ -n $previous ]]; then delta=$((used - previous)); printf '  %-28s used=%s bytes (%+d since prior sample)\n' "$mount" "$used" "$delta"
  else printf '  %-28s used=%s bytes (baseline)\n' "$mount" "$used"; fi
done < <(df -P -B1 -- 2>/dev/null || df -P -B1)
log INFO 'Storage growth sample recorded.'
