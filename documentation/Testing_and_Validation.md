# Testing and Validation

## Environment and command

The test suite was run in Kali Linux on WSL 2 from the project directory. This validates the Linux collection and reporting path in Kali WSL; it does not claim an Ubuntu host run. The runner skips live collection only on MSYS/MINGW/Cygwin, so all Linux integration checks ran here.

```bash
cd /mnt/d/Linuxproj/linux-storage-monitor
./tests/run_tests.sh
```

The saved transcript is [`../tests/test_results.txt`](../tests/test_results.txt). The integration run also created [`../logs/test-run.log`](../logs/test-run.log), a CSV sample at [`../data/storage_history.csv`](../data/storage_history.csv), and the generated report [`storage_report_20261102_101427.txt`](../reports/storage_report_20261102_101427.txt).

## Results

| Test | Command or check | Result |
|---|---|---|
| Configuration readable | `test -r config/monitor.conf` | PASS |
| Main runner executable | `test -x bin/run_all.sh` | PASS |
| Threshold endpoints | Regex accepts 0 and 100 | PASS |
| Threshold upper bound | Regex rejects 101 | PASS |
| Bash syntax | `bash -n` on installer, modules, and library | PASS |
| Disk, inode, growth, and report cycle | `bin/run_all.sh` | PASS (Kali WSL) |
| CSV header and sample | Check `data/storage_history.csv` has at least two lines | PASS (Kali WSL) |
| Generated report | Check for `reports/storage_report_*.txt` | PASS (Kali WSL) |
| Warning and critical alerts | `check_threshold` helper branches | PASS |
| Backup archive integrity | `tar -tzf` on generated archive | PASS |
| Selected-file recovery | Restore into `backup/test-recovery` | PASS |
| Unsafe destination rejection | Reject `../outside` restore destination | PASS |

Cron scheduling, installer permission modes, and terminal screenshot capture were not covered by this test run. The report retains screenshot placeholders; the executed command and transcript are included here and in Appendix D of the academic report.

## Captured test output

```text
PASS: configuration file readable
PASS: main runner executable
PASS: threshold parser accepts zero and 100
PASS: threshold parser rejects 101
PASS: monitor scripts pass Bash parser
PASS: disk, inode, growth and report cycle completes
PASS: CSV header and at least one sample
PASS: generated report exists
PASS: warning and critical alert branches execute
PASS: compressed backup passes tar integrity check
PASS: selected project files recover
PASS: unsafe destination rejected

Test summary: 12 passed, 0 failed
```
