# Linux Storage Monitoring System

Project 7 from the Linux Infrastructure Deployment Project Sample Problem Statements. This Bash utility monitors mounted filesystems, inode use, growth history, configurable thresholds, reports, and verified compressed backups.

## Requirements

Ubuntu 20.04 or newer is recommended. The scripts use Bash, GNU `df`, `du`, `stat`, `awk`, `grep`, `sort`, `tail`, `date`, `tar`, and `gzip`; cron is needed only for scheduling. They run as the installing user and do not need root for ordinary scans. Avoid running as root unless system-wide log ownership is specifically required.

Install dependencies on Ubuntu:

```bash
sudo apt update
sudo apt install -y bash coreutils findutils gawk sed grep tar gzip cron unzip
```

## First run(1st)

```bash
unzip ~/Downloads/linux-storage-monitor.zip -d "$HOME"
cd "$HOME/linux-storage-monitor"
chmod +x install.sh bin/*.sh bin/lib/*.sh tests/*.sh
./install.sh
./bin/run_all.sh
```

`run_all.sh` runs disk and inode scans, stores one CSV sample, and writes a report. Output is under `logs/`, `data/`, and `reports/`.

See [EXECUTION_GUIDE.md](EXECUTION_GUIDE.md) for a beginner walkthrough, cron setup, verification, backup, and recovery commands.

## Configuration

Edit `config/monitor.conf`. Thresholds are integer percentages from 0 through 100; warning must be below critical. Paths must be relative to the project. The config is parsed as data rather than sourced as executable shell code. Default disk and inode warning/critical thresholds are 75% and 90%.

## Modules

* `bin/disk_monitor.sh` — `df -P -B1` capacity view and disk threshold alerts.
* `bin/inode_monitor.sh` — `df -P -i` inode view and inode threshold alerts.
* `bin/storage_growth.sh` — timestamped samples in `data/storage_history.csv`, with used-byte delta from the previous sample.
* `bin/alert_monitor.sh` — runs disk and inode alert checks.
* `bin/generate_report.sh` — text report with disk/inode data, largest top-level directories, recent alerts, and history.
* `bin/monitor_cycle.sh` — cron's five-minute monitoring cycle.
* `bin/backup_project.sh`, `bin/restore_backup.sh` — verified gzip tar archive and recovery restricted to the configured backup directory.

## Security notes

The project is intended to be owned by one user, with scripts set to mode 750 and logs, configuration, and history set to mode 640. Thresholds and paths are validated. Configuration is parsed as data, never sourced as shell code. Recovery is restricted to archives and destinations inside this project's backup folder, including symlink resolution. Directory size scanning is best effort; permission-denied paths are omitted from report output.

## Test and evidence

Run `./tests/run_tests.sh` on Ubuntu. Cron is configured per user by `./bin/install_cron.sh`; it requires the cron service and a working `crontab` command. The `screenshots/` directory contains instructions for capturing the required genuine Ubuntu terminal evidence. The development host for the supplied project artifacts was Windows, so Ubuntu screenshots and cron runtime evidence must be captured on the target Linux host.

