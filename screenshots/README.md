# Screenshot evidence capture

The documentation was authored on Windows and no Ubuntu desktop was available. No terminal screenshots are fabricated. Capture these twelve views on the target Ubuntu machine and save numbered PNGs in this directory:

1. Environment: `uname -a; cat /etc/os-release`
2. Project tree: `find . -maxdepth 3 -type f -print | sort`
3. Installer: `./install.sh` after prerequisites are present
4. Disk scan: `./bin/disk_monitor.sh`
5. Inode scan: `./bin/inode_monitor.sh`
6. Growth/history: `./bin/storage_growth.sh; tail -n 8 data/storage_history.csv`
7. Alert: save monitor.conf, lower a warning limit below observed use, run the relevant monitor, then restore the saved file. Do not fill storage.
8. Report: `./bin/generate_report.sh; latest=$(ls -1t reports/*.txt | head -1); head -n 45 "$latest"`
9. Cron: `crontab -l; tail -n 20 logs/cron.log` after at least one schedule fires
10. Backup creation: `./bin/backup_project.sh; ls -lh backup/*.tar.gz`
11. Archive integrity: `tar -tzf "$archive" | head`
12. Recovery: `./bin/restore_backup.sh "$archive" backup/demo-recovery; find backup/demo-recovery -maxdepth 2 -type f -print`

Use a readable terminal font and crop unrelated desktop area. Insert the images at Figures 4.1–4.12 in the report. Restore the normal threshold immediately after the alert capture.
