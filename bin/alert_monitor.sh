#!/usr/bin/env bash
set -Eeuo pipefail
source "$(dirname -- "$0")/lib/common.sh"
load_config
"${PROJECT_ROOT}/bin/disk_monitor.sh"
"${PROJECT_ROOT}/bin/inode_monitor.sh"
printf 'Alerts: %s\n' "${PROJECT_ROOT}/${ALERT_LOG}"
