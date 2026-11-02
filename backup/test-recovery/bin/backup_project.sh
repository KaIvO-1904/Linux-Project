#!/usr/bin/env bash
set -Eeuo pipefail
source "$(dirname -- "$0")/lib/common.sh"
load_config
stamp=$(date '+%Y%m%d_%H%M%S')
archive="${PROJECT_ROOT}/${BACKUP_DIR}/linux-storage-monitor_${stamp}.tar.gz"
tar -czf "$archive" -C "$PROJECT_ROOT" bin config data tests tools README.md EXECUTION_GUIDE.md install.sh system_architecture.png
tar -tzf "$archive" >/dev/null
printf 'Backup created and verified: %s\n' "$archive"
log INFO "Backup created and integrity verified: ${archive#${PROJECT_ROOT}/}"
