#!/usr/bin/env bash
set -Eeuo pipefail
source "$(dirname -- "$0")/lib/common.sh"
load_config
[[ $# == 2 ]] || { echo "Usage: $0 BACKUP_ARCHIVE DESTINATION_DIRECTORY" >&2; exit 2; }
archive=$(realpath -e -- "$1")
backup_root=$(realpath -e -- "${PROJECT_ROOT}/${BACKUP_DIR}")
[[ $backup_root == "${PROJECT_ROOT}/${BACKUP_DIR}" || $backup_root == "${PROJECT_ROOT}/${BACKUP_DIR}"/* ]] || die 'Configured backup directory resolves outside the project.'
[[ $archive == "$backup_root"/* && -f $archive ]] || die 'Archive must be a file inside the configured backup directory.'
[[ $2 != /* && $2 != *'..'* && $2 =~ ^[A-Za-z0-9_./-]+$ ]] || die 'Destination must be a safe relative path.'
destination="${PROJECT_ROOT}/$2"
[[ $destination == "$backup_root"/* ]] || die 'Recovery destination must be below the configured backup directory.'
check_path=$PROJECT_ROOT
IFS='/' read -r -a parts <<< "$2"
for part in "${parts[@]}"; do
  [[ -n $part ]] || continue
  check_path="${check_path}/${part}"
  [[ ! -L $check_path ]] || die 'Recovery destination cannot traverse a symbolic link.'
done
mkdir -p "$destination"
destination=$(realpath -e -- "$destination")
[[ $destination == "$backup_root"/* ]] || die 'Recovery destination must resolve inside the configured backup directory.'
tar -tzf "$archive" >/dev/null
tar -xzf "$archive" -C "$destination" --no-same-owner
printf 'Recovered selected project files to: %s\n' "$destination"
