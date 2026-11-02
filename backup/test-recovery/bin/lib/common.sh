#!/usr/bin/env bash
set -Eeuo pipefail

PROJECT_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd -P)"
CONFIG_FILE="${PROJECT_ROOT}/config/monitor.conf"

log() { printf '%s [%s] %s\n' "$(date '+%Y-%m-%d %H:%M:%S%z')" "$1" "$2" | tee -a "${PROJECT_ROOT}/${MONITOR_LOG}"; }
die() { printf 'ERROR: %s\n' "$*" >&2; exit 1; }
valid_percent() { [[ ${1:-} =~ ^([0-9]|[1-9][0-9]|100)$ ]]; }
valid_relpath() { [[ $1 != /* && $1 != *'..'* && $1 =~ ^[A-Za-z0-9_./-]+$ ]]; }

load_config() {
  [[ -r "$CONFIG_FILE" ]] || die "Configuration not readable: $CONFIG_FILE"
  WARNING_THRESHOLD=75 CRITICAL_THRESHOLD=90 INODE_WARNING_THRESHOLD=75 INODE_CRITICAL_THRESHOLD=90
  REPORT_TOP_N=10 EXCLUDED_FILESYSTEM_TYPES=tmpfs,devtmpfs,squashfs,overlay
  ALERT_LOG=logs/administrator_alerts.log MONITOR_LOG=logs/storage_monitor.log
  HISTORY_CSV=data/storage_history.csv REPORT_DIR=reports BACKUP_DIR=backup
  local key value
  while IFS='=' read -r key value || [[ -n ${key:-} ]]; do
    [[ $key =~ ^[A-Z_]+$ ]] || continue
    value=${value%%#*}; value=${value//[[:space:]]/}
    case "$key" in
      WARNING_THRESHOLD|CRITICAL_THRESHOLD|INODE_WARNING_THRESHOLD|INODE_CRITICAL_THRESHOLD)
        valid_percent "$value" || die "Invalid $key (expected integer 0-100)"; printf -v "$key" '%s' "$value" ;;
      REPORT_TOP_N) [[ $value =~ ^[1-9][0-9]?$ ]] || die 'REPORT_TOP_N must be 1-99'; REPORT_TOP_N=$value ;;
      EXCLUDED_FILESYSTEM_TYPES) [[ $value =~ ^[A-Za-z0-9_,.-]+$ ]] || die 'Invalid filesystem type list'; EXCLUDED_FILESYSTEM_TYPES=$value ;;
      ALERT_LOG|MONITOR_LOG|HISTORY_CSV|REPORT_DIR|BACKUP_DIR)
        valid_relpath "$value" || die "Invalid relative path in $key"; printf -v "$key" '%s' "$value" ;;
      *) : ;;
    esac
  done < "$CONFIG_FILE"
  (( WARNING_THRESHOLD < CRITICAL_THRESHOLD )) || die 'WARNING_THRESHOLD must be lower than CRITICAL_THRESHOLD'
  (( INODE_WARNING_THRESHOLD < INODE_CRITICAL_THRESHOLD )) || die 'INODE_WARNING_THRESHOLD must be lower than INODE_CRITICAL_THRESHOLD'
  mkdir -p "${PROJECT_ROOT}/$(dirname "$ALERT_LOG")" "${PROJECT_ROOT}/$(dirname "$MONITOR_LOG")" \
    "${PROJECT_ROOT}/$(dirname "$HISTORY_CSV")" "${PROJECT_ROOT}/${REPORT_DIR}" "${PROJECT_ROOT}/${BACKUP_DIR}"
  touch "${PROJECT_ROOT}/${MONITOR_LOG}" "${PROJECT_ROOT}/${ALERT_LOG}"
}

alert() {
  local level=$1 metric=$2 mount=$3 pct=$4 limit=$5
  local message="${level}: ${metric} usage on ${mount} is ${pct}% (threshold ${limit}%)"
  printf '%s %s\n' "$(date '+%Y-%m-%d %H:%M:%S%z')" "$message" | tee -a "${PROJECT_ROOT}/${ALERT_LOG}" "${PROJECT_ROOT}/${MONITOR_LOG}" >&2
}

check_threshold() {
  local metric=$1 mount=$2 pct=$3 warning=$4 critical=$5
  if (( pct >= critical )); then alert CRITICAL "$metric" "$mount" "$pct" "$critical"
  elif (( pct >= warning )); then alert WARNING "$metric" "$mount" "$pct" "$warning"
  fi
}

excluded_fs() { [[ ",$EXCLUDED_FILESYSTEM_TYPES," == *",$1,"* ]]; }
init_history() {
  local f="${PROJECT_ROOT}/${HISTORY_CSV}"
  [[ -s $f ]] || printf 'timestamp,filesystem,mountpoint,total_bytes,used_bytes,available_bytes,usage_percent,inodes_total,inodes_used,inodes_free,inode_percent\n' > "$f"
}
