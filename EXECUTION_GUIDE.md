# Execution Guide (Ubuntu)

These commands assume you copied `linux-storage-monitor.zip` from the supplied deliverables to `~/Downloads` on the Ubuntu computer. Run them in Ubuntu Terminal as your regular account.

## 1. Install prerequisites and enter the project

```bash
sudo apt update
sudo apt install -y bash coreutils findutils gawk sed grep tar gzip cron unzip
unzip ~/Downloads/linux-storage-monitor.zip -d "$HOME"
cd "$HOME/linux-storage-monitor"
chmod +x install.sh bin/*.sh bin/lib/*.sh tests/*.sh
./install.sh
```

The installer checks for Ubuntu/Debian, creates runtime folders and files, and sets private file modes. It does not require root. The `apt` commands use `sudo` because package installation is a system operation.

## 2. Configure and run the complete system

```bash
nano config/monitor.conf
./bin/run_all.sh
```

Default alerts begin at 75% (warning) and 90% (critical), separately for blocks and inodes. `run_all.sh` prints disk and inode tables, records the sample in CSV, and creates a timestamped report.

## 3. Run individual modules

```bash
./bin/disk_monitor.sh
./bin/inode_monitor.sh
./bin/storage_growth.sh
./bin/alert_monitor.sh
./bin/generate_report.sh
```

`alert_monitor.sh` repeats the disk and inode threshold checks. On a safe test, change thresholds temporarily to a value known to be below the current usage, observe the warning, then restore the normal values. Do not create large files to fill a filesystem.

## 4. Inspect output

```bash
column -s, -t < data/storage_history.csv | tail -n 15
tail -n 50 logs/administrator_alerts.log
tail -n 50 logs/storage_monitor.log
ls -lh reports/
cat reports/storage_report_*.txt
```

To see a size ranking for one selected directory without scanning the whole host:

```bash
du -h --max-depth=1 "$HOME" 2>/dev/null | sort -h | tail -n 10
find "$HOME" -maxdepth 2 -type f -printf '%s %p\n' 2>/dev/null | sort -n | tail -n 10
```

## 5. Enable cron

Start cron and install per-user entries:

```bash
sudo systemctl enable --now cron
./bin/install_cron.sh
crontab -l
```

Monitoring (disk, inode, and history) runs every five minutes. Reports run every fifteen minutes. Check cron service and execution evidence with:

```bash
systemctl status cron --no-pager
grep 'LINUX_STORAGE_MONITOR' <(crontab -l)
tail -f logs/cron.log
```

Ubuntu syslog may also record cron dispatches:

```bash
grep CRON /var/log/syslog | tail -n 30
```

The user must remain the owner of the project because cron runs with that user's permissions. If using a different install location, reinstall the crontab after moving the directory.

## 6. Backup and recovery demonstration

```bash
./bin/backup_project.sh
ls -lh backup/*.tar.gz
tar -tzf "$(ls -1t backup/*.tar.gz | head -n 1)" | head
mkdir -p backup/demo-recovery
./bin/restore_backup.sh "$(ls -1t backup/*.tar.gz | head -n 1)" backup/demo-recovery
find backup/demo-recovery -maxdepth 2 -type f -print
```

Recovery writes a copy under `backup/` and rejects destinations outside that directory, including symlink escapes. It does not overwrite system files. Keep original data untouched during the demonstration.

## 7. Run project checks and inspect permissions

```bash
./tests/run_tests.sh
stat -c '%a %n' install.sh bin/*.sh config/monitor.conf logs/*.log data/storage_history.csv
```

The automated test script checks config presence, threshold input boundaries, CSV header, backup integrity and recovery, and path rejection. Disk/inode observations depend on the current host. Cron timing requires waiting for a scheduled interval and is verified separately above.

## 8. Faculty demonstration order

1. Show `uname -a`, `ls -R`, and `config/monitor.conf`.
2. Run `./bin/disk_monitor.sh` and `./bin/inode_monitor.sh`.
3. Run `./bin/storage_growth.sh` twice and show `data/storage_history.csv`.
4. Temporarily lower a warning threshold to trigger a real alert from existing use; restore config immediately.
5. Generate and open a report.
6. Show `crontab -l` and `logs/cron.log` after one interval.
7. Create a backup, list archive contents, recover to `backup/demo-recovery`, and compare a recovered file.

Capture screenshots with the commands listed in `screenshots/README.md`. Screenshots should be taken on Ubuntu so the evidence represents the target environment.
