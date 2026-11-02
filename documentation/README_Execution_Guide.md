# README — Execution Guide

## Scope and host status

This project targets Ubuntu Linux (Ubuntu 20.04 or newer is recommended). The recorded integration run was executed in Kali Linux on WSL 2 and completed live collection and report-generation checks. Kali WSL evidence is not an Ubuntu run. Cron timing, installer permissions, and genuine terminal screenshots remain to be collected. The ZIP should be copied to `~/Downloads` on Ubuntu.

## Install and start

```bash
sudo apt update
sudo apt install -y bash coreutils findutils gawk sed grep tar gzip cron unzip
unzip ~/Downloads/linux-storage-monitor.zip -d "$HOME"
cd "$HOME/linux-storage-monitor"
chmod +x install.sh bin/*.sh bin/lib/*.sh tests/*.sh
./install.sh
./bin/run_all.sh
```

The installer checks `/etc/os-release`, checks command presence, creates runtime directories and the CSV header, and attempts mode 750 for scripts/directories and 640 for config/data/logs. It prints package guidance if utilities are missing; it does not install packages. Inspect the mode results with `stat -c '%a %n' ...`. The installer's `chmod ... || true` clauses can hide failures, so check each result.

## Run modules

```bash
./bin/disk_monitor.sh
./bin/inode_monitor.sh
./bin/storage_growth.sh
./bin/alert_monitor.sh
./bin/generate_report.sh
./tests/run_tests.sh
```

Edit `config/monitor.conf` to change block/inode warning and critical percentages. Values must be integer 0–100; each warning must remain below its critical threshold. `run_all.sh` performs disk, inode, CSV growth, and text report work in sequence.

## Inspect files

```bash
column -s, -t < data/storage_history.csv | tail -n 15
tail -n 50 logs/administrator_alerts.log
tail -n 50 logs/storage_monitor.log
ls -lh reports/
cat reports/storage_report_*.txt
find . -maxdepth 3 -type f -print | sort
```

CSV has one row per included mountpoint per sample. The first sample is a baseline; later rows print the change in used bytes since the previous sample.

## Cron: 5-minute monitoring / 15-minute report

```bash
sudo systemctl enable --now cron
./bin/install_cron.sh
crontab -l
systemctl status cron --no-pager
tail -f logs/cron.log
```

The monitor cycle collects disk/inode data and appends growth history every five minutes. Report generation runs every fifteen minutes. Cron commands run under the current user's account. The installer preserves unrelated entries and replaces only lines tagged `LINUX_STORAGE_MONITOR`. Wait for at least one matching interval before treating this as runtime-verified.

## Backup and recovery

```bash
./bin/backup_project.sh
archive=$(ls -1t backup/linux-storage-monitor_*.tar.gz | head -n 1)
tar -tzf "$archive" | head
mkdir -p backup/demo-recovery
./bin/restore_backup.sh "$archive" backup/demo-recovery
find backup/demo-recovery -maxdepth 2 -type f -print
```

The archive covers scripts, configuration, data, tests, documentation sources, guides, and architecture image. It is listed with `tar -tzf` before success is reported. Recovery requires an archive under the configured backup directory and a destination below `backup/`; parent traversal and symbolic-link path components are rejected.

## Faculty demonstration and evidence screenshots

Capture these twelve genuine terminal views in `screenshots/` and caption them as Figures 4.1–4.12 in the report. Use Ubuntu Terminal and crop away unrelated desktop content.

1. Environment: `uname -a; cat /etc/os-release`
2. Tree: `find . -maxdepth 3 -type f -print | sort`
3. Installation: show the completed `./install.sh` output (also show apt package command if required).
4. Disk: `./bin/disk_monitor.sh`
5. Inodes: `./bin/inode_monitor.sh`
6. Growth: `./bin/storage_growth.sh; tail -n 8 data/storage_history.csv`
7. Alert: save config, temporarily lower a warning threshold below observed use, run the corresponding monitor, then restore config: `cp config/monitor.conf /tmp/monitor.conf.saved`; edit with `nano`; run module; `cp /tmp/monitor.conf.saved config/monitor.conf`. Do not fill a filesystem.
8. Report: `./bin/generate_report.sh; latest=$(ls -1t reports/*.txt | head -1); head -n 45 "$latest"`
9. Cron: `crontab -l; tail -n 20 logs/cron.log` after jobs have fired.
10. Backup creation: `./bin/backup_project.sh; ls -lh backup/*.tar.gz`
11. Integrity: `tar -tzf "$archive" | head`
12. Recovery: `./bin/restore_backup.sh "$archive" backup/demo-recovery; find backup/demo-recovery -maxdepth 2 -type f -print`

No screenshot is embedded as if captured. Run `./tests/run_tests.sh` and retain its actual transcript. Then update DOCX fields (Ctrl+A, F9 in Word), check page numbers after the fields refresh, fill placeholders, and export a reviewed PDF if pagination changes.
