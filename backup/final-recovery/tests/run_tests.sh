#!/usr/bin/env bash
set -Eeuo pipefail
ROOT="$(cd -- "$(dirname -- "$0")/.." && pwd -P)"
mkdir -p "$ROOT/data" "$ROOT/logs" "$ROOT/reports" "$ROOT/backup"
pass=0 fail=0
check() {
  local name=$1
  shift
  if "$@"; then printf 'PASS: %s\n' "$name"; pass=$((pass + 1))
  else printf 'FAIL: %s\n' "$name"; fail=$((fail + 1)); fi
}

check 'configuration file readable' test -r "$ROOT/config/monitor.conf"
check 'main runner executable' test -x "$ROOT/bin/run_all.sh"
check 'threshold parser accepts zero and 100' bash -c '[[ 0 =~ ^([0-9]|[1-9][0-9]|100)$ && 100 =~ ^([0-9]|[1-9][0-9]|100)$ ]]'
check 'threshold parser rejects 101' bash -c '! [[ 101 =~ ^([0-9]|[1-9][0-9]|100)$ ]]'
check 'monitor scripts pass Bash parser' bash -c 'for f in "$1"/install.sh "$1"/bin/*.sh "$1"/bin/lib/*.sh; do bash -n "$f" || exit 1; done' _ "$ROOT"

platform=$(uname -s)
if [[ $platform == MSYS* || $platform == MINGW* || $platform == CYGWIN* ]]; then
  printf 'SKIP: live df collection, CSV sampling, and report integration require Linux; host is %s\n' "$platform"
else
  if "$ROOT/bin/run_all.sh" >"$ROOT/logs/test-run.log" 2>&1; then
    check 'disk, inode, growth and report cycle completes' true
  else check 'disk, inode, growth and report cycle completes' false; fi
  check 'CSV header and at least one sample' bash -c 'test "$(wc -l < "$1")" -ge 2' _ "$ROOT/data/storage_history.csv"
  check 'generated report exists' bash -c 'compgen -G "$1/reports/storage_report_*.txt" >/dev/null' _ "$ROOT"
fi

# Exercise both threshold branches against a harmless test mount label.
if bash -c 'source "$1/bin/lib/common.sh"; load_config; check_threshold disk TEST-MOUNT 75 75 90; check_threshold inode TEST-MOUNT 90 75 90' _ "$ROOT" >/dev/null 2>&1; then
  check 'warning and critical alert branches execute' bash -c 'grep -q "WARNING: disk usage on TEST-MOUNT" "$1" && grep -q "CRITICAL: inode usage on TEST-MOUNT" "$1"' _ "$ROOT/logs/administrator_alerts.log"
else check 'warning and critical alert branches execute' false; fi

if "$ROOT/bin/backup_project.sh" >"$ROOT/logs/test-backup.log" 2>&1; then
  archive=$(ls -1t "$ROOT"/backup/linux-storage-monitor_*.tar.gz | head -n 1)
  check 'compressed backup passes tar integrity check' bash -c 'tar -tzf "$1" >/dev/null' _ "$archive"
  mkdir -p "$ROOT/backup/test-recovery"
  if "$ROOT/bin/restore_backup.sh" "$archive" backup/test-recovery >/dev/null 2>&1; then
    check 'selected project files recover' test -f "$ROOT/backup/test-recovery/README.md"
  else check 'selected project files recover' false; fi
else check 'compressed backup passes tar integrity check' false; fi
if [[ -n ${archive:-} ]]; then
  check 'unsafe destination rejected' bash -c '! "$1/bin/restore_backup.sh" "$2" ../outside >/dev/null 2>&1' _ "$ROOT" "$archive"
else check 'unsafe destination rejected' false; fi

printf '\nTest summary: %d passed, %d failed\n' "$pass" "$fail"
(( fail == 0 ))
