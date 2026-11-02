#!/usr/bin/env python3
"""Build the audited academic report and companion guidance from project sources."""
from pathlib import Path
import re
from PIL import Image as PILImage, ImageDraw, ImageFont
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_CELL_VERTICAL_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Image, Preformatted, KeepTogether)
from reportlab.platypus.tableofcontents import TableOfContents

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'documentation'
OUT.mkdir(exist_ok=True)
DOCX_PATH = OUT / 'Linux_Storage_Monitoring_System_Report.docx'
PDF_PATH = OUT / 'Linux_Storage_Monitoring_System_Report.pdf'
ARCH = ROOT / 'system_architecture.png'
FIGURES = [
    '3.1 System architecture of the implemented storage monitor',
    '3.2 Audited project directory structure',
    '4.1 Ubuntu terminal environment (capture on target host)',
    '4.2 Project directory structure (capture on target host)',
    '4.3 Installation process (capture on target host)',
    '4.4 Disk monitoring output (capture on target host)',
    '4.5 Inode monitoring output (capture on target host)',
    '4.6 Storage history and growth sample (capture on target host)',
    '4.7 Warning and critical alert output (capture on target host)',
    '4.8 Generated text report (capture on target host)',
    '4.9 Cron configuration and execution log (capture on target host)',
    '4.10 Timestamped backup creation (capture on target host)',
    '4.11 Compressed archive integrity check (capture on target host)',
    '4.12 Selected-file recovery (capture on target host)',
]
TABLES = ['2.1 Utilities used by the implementation', '3.1 Project directory and file roles', '4.1 Test and validation results']

def architecture_diagram():
    W,H=1600,1050
    im=PILImage.new('RGB',(W,H),'white'); d=ImageDraw.Draw(im)
    fp='C:/Windows/Fonts/times.ttf'; fpb='C:/Windows/Fonts/timesbd.ttf'
    title=ImageFont.truetype(fpb,38); head=ImageFont.truetype(fpb,25); body=ImageFont.truetype(fp,22)
    d.text((W//2,28),'LINUX STORAGE MONITORING SYSTEM — IMPLEMENTED FLOW',font=title,fill='#20252a',anchor='mt')
    def box(x,y,w,h,heading,lines,fill='#fbfbfb'):
        d.rounded_rectangle((x,y,x+w,y+h),radius=14,fill=fill,outline='#697783',width=3)
        d.text((x+w//2,y+15),heading,font=head,fill='#20252a',anchor='mt')
        for i,line in enumerate(lines): d.text((x+16,y+58+i*30),line,font=body,fill='#303840')
    def arrow(a,b,label=None):
        import math
        d.line((a,b),fill='#425c70',width=5)
        angle=math.atan2(b[1]-a[1],b[0]-a[0]); L=18
        d.polygon((b,(b[0]-L*math.cos(angle-.5),b[1]-L*math.sin(angle-.5)),(b[0]-L*math.cos(angle+.5),b[1]-L*math.sin(angle+.5))),fill='#425c70')
        if label: d.text(((a[0]+b[0])//2,(a[1]+b[1])//2-22),label,font=body,fill='#303840',anchor='mm')
    box(45,210,280,190,'Linux OS / Ubuntu',['Mounted filesystems','Block and inode counters'])
    box(390,175,365,260,'Collection scripts',['disk_monitor.sh: df blocks','inode_monitor.sh: df -i','storage_growth.sh: CSV'])
    box(390,520,365,220,'Shared validation',['common.sh reads monitor.conf','Percent and path validation','Warning / critical decision'])
    box(850,120,300,175,'Threshold alerts',['Disk and inode checks','Alert messages'])
    box(850,355,300,175,'Storage history',['CSV timestamps','Prior-used-byte delta'])
    box(1250,120,300,175,'Log files',['administrator_alerts.log','storage_monitor.log'])
    box(1250,355,300,175,'Text reports',['df blocks and inodes','du ranking, alerts, CSV'])
    box(850,700,300,175,'Cron automation',['5 min: monitor_cycle.sh','15 min: generate_report.sh'])
    box(1250,700,300,175,'Backup / recovery',['tar + gzip; list check','Restore below backup/'])
    arrow((325,290),(390,290)); arrow((570,435),(570,520),'threshold rules')
    arrow((755,575),(850,205)); arrow((755,620),(850,440)); arrow((1150,205),(1250,205))
    arrow((1150,440),(1250,440)); arrow((1000,700),(700,435),'scheduled calls')
    arrow((1150,790),(1250,790),'manual backup')
    d.text((W//2,H-35),'Conceptual data/control flow derived from the inspected Bash source; no runtime values are implied.',font=body,fill='#555',anchor='mm')
    im.save(ARCH)

architecture_diagram()

# Content blocks use actual implementation facts; evidence claims refer to the saved transcript.
CHAPTERS = [
('1. INTRODUCTION', [
('1.1 Aim', ['The aim of this project is to provide an auditable Bash toolset for monitoring mounted filesystem block capacity and inode use, recording repeated measurements, raising threshold-based administrator alerts, and producing a text summary. The implementation is project-scoped and intended to run as the ordinary account that owns the files.']),
('1.2 Background', ['Linux storage capacity has at least two operational dimensions. Data blocks hold file contents, while inodes hold file metadata and directory references. A filesystem may have available bytes but too few free inodes to create more files. Conversely, high block consumption can prevent writes even when inode capacity remains. A single manual command offers a snapshot; a scheduled sample history helps reveal whether use is changing.', 'The supplied reference report uses Bash and standard Linux utilities to illustrate these tasks. This report follows its chapter order and academic presentation while describing the scripts and test evidence in the current workspace.']),
('1.3 Problem Statement', ['Administrators need a repeatable way to inspect filesystem capacity and inode consumption, compare values with warning and critical limits, retain dated observations, and review reports and alerts. The delivered project implements those mechanisms. Its current Windows authoring environment did not provide a usable Ubuntu runtime, so live Linux measurements and cron timing have not been demonstrated in the recorded results.']),
('1.4 Objectives', ['The objectives are to collect disk and inode usage from mounted filesystems; filter configured pseudo-filesystem types; compare percentages against separate disk and inode thresholds; write timestamps and capacity figures to CSV; compare used bytes with the previous sample; keep monitor and administrator alert logs; produce a timestamped text report; install per-user cron jobs; and create, verify, and recover a compressed project archive.'])]),
('2. METHODOLOGY', [
('2.1 Tools and Technologies Used', ['The scripts target Ubuntu or a compatible Debian-derived Linux. Bash provides strict-mode execution, functions, arrays, arithmetic comparisons, process substitution, and configuration parsing. GNU df reports filesystem capacity and inode counts; stat identifies filesystem types; awk reads the previous CSV sample; du, sort, and tail prepare a best-effort directory-size ranking in the report. date supplies timestamps; tee appends log entries while displaying alerts; tar and gzip create compressed backups; realpath and symbolic-link checks constrain recovery; cron and crontab provide per-user scheduling.', 'The installer also uses find and chmod to set script permissions. grep is used when installing marked cron lines; ls is used in test and operator commands. sed appears in the dependency guidance but is not called by the project scripts. CSV is a plain comma-separated history file, not a database. Python, python-docx, ReportLab, and Pillow were used to prepare the documentation artifacts; they are not runtime dependencies of the monitor.']),
('2.1.1 Utilities Used by the Implementation', ['Table 2.1 distinguishes commands used by project code from those used only in operator instructions or package guidance.']),
('2.2 Approach / Development Process', ['The workspace implementation is organized around a shared library and small command-line modules. First, the requested behavior was mapped to disk collection, inode collection, sampling, alerts, reports, cron, and backup/recovery. Configuration was separated from code. The scripts were then connected through run_all.sh and monitor_cycle.sh. A safe test script checks parser syntax, simple threshold boundaries, alert branches, tar listing, a project-local recovery copy, and unsafe destination rejection. It detects MSYS and skips Linux-only collection checks rather than treating Windows volumes as Linux evidence.', 'Validation is limited to what the transcript records. The final suite ran under Git for Windows Bash and reported 9 passed, 0 failed, with Linux-only live collection skipped. This confirms syntax and selected helper/archive paths, but it does not establish Ubuntu disk output, generated monitoring reports, cron execution, or Linux permissions.'])]),
('3. LINUX SYSTEM ADMINISTRATION — DESIGN AND IMPLEMENTATION', [
('3.1 System Architecture', ['Figure 3.1 shows the control and data paths visible in the source. The Linux host supplies filesystem statistics. Disk, inode, and growth scripts gather those statistics; common.sh parses thresholds and emits alerts; growth samples are appended to CSV; the report combines df, du, alert, and history output. Cron invokes a five-minute monitoring cycle and a fifteen-minute report command. Backup and recovery are separate project-local commands. The diagram represents code structure, not a captured runtime.']),
('3.2 Linux Environment Setup', ['The target is Ubuntu 20.04 or newer, as stated by the project README. The installer reads /etc/os-release and accepts Ubuntu or an ID_LIKE value containing Debian. It checks for Bash, df, du, find, ls, awk, sed, grep, date, tar, gzip, stat, sort, tail, and hostname. If utilities are missing, it prints an apt installation command; it does not automatically install packages.', 'The current development host is Windows with Git for Windows Bash. WSL returned access denied. The installer was not run on Ubuntu, so no Ubuntu release, package versions, or Linux host settings are claimed. The companion guide contains the exact extraction, dependency, installer, and first-run commands.']),
('3.3 User and Group Management', ['No project-specific Linux user or group is created. The code runs as the invoking account. Cron entries are installed in that account’s personal crontab, so the account must continue to own and access the project. The project has no shared-directory or group-membership demonstration; report descriptions of user/group configuration are therefore limited to this fact.']),
('3.4 File and Directory Management', ['The repository separates executable modules, configuration, data, logs, reports, backups, tests, screenshots, and documentation. The current CSV contains only its header. The logs were cleared after helper testing; no live filesystem measurement is stored. Reports is empty because generate_report.sh was not run against Linux data. The backup directory contains a verified archive and a recovery copy produced by the Git Bash test.', 'Figure 3.2 and Table 3.1 summarize the current project layout. The archive and recovery copy are test artifacts; documentation placeholders are not represented as collected screenshots.']),
('3.5 Package and Process Management', ['The installer checks for command availability and reports apt guidance if required utilities are missing. It does not install packages, enable services, or create a long-running process. Interactive commands exit after a scan. Cron is optional and invokes short-lived scripts. The cron installer rewrites only lines tagged with LINUX_STORAGE_MONITOR and retains other crontab lines. Cron service status and runtime dispatch have not been checked on Ubuntu.']),
('3.6 Storage and File System Configuration', ['The project does not partition disks, create filesystems, resize logical volumes, mount devices, or change fstab. disk_monitor.sh uses df -P -B1 for byte totals and percentages; inode_monitor.sh uses df -P -i. Both remove the percent suffix, identify filesystem type with stat -f -c %T, skip types in EXCLUDED_FILESYSTEM_TYPES, print a table, and invoke the common threshold comparison. These commands operate on available mount statistics and do not intentionally create storage pressure.', 'The configured defaults are 75% warning and 90% critical for both block and inode use. Values are integer percentages from 0 to 100; warning must be lower than critical. The output and alerts are per mounted filesystem. No current disk or inode percentages are reported because the Windows df output was not used as Linux evidence.']),
('3.7 Backup and Automation', ['storage_growth.sh initializes the CSV header if the file is absent or empty. For each included mountpoint, it appends timestamp, filesystem, mountpoint, total/used/available bytes, usage percent, and inode totals/used/free/percent. It then uses awk to find the prior row for that mountpoint and prints the signed used-byte difference; the first sample is described as a baseline. The existing CSV contains only the header, so there is no historical comparison result.', 'install_cron.sh adds a monitor_cycle.sh entry every five minutes and a generate_report.sh entry every fifteen minutes. Both append output to logs/cron.log. The crontab was not installed or observed in the tested environment.', 'generate_report.sh writes a timestamped report with df -hP, df -iP, a best-effort du ranking of top-level directories on the root filesystem, the last 50 alert lines, and the last 20 CSV lines. The runtime report directory is empty in the current workspace.', 'backup_project.sh packages bin, config, data, tests, tools, README.md, EXECUTION_GUIDE.md, install.sh, and the architecture diagram, then runs tar -tzf to check that the archive can be listed. The recorded Git Bash test passed this integrity check and extracted selected files into backup/test-recovery. restore_backup.sh restricts the archive to the configured backup directory, requires a relative destination below backup/, rejects symbolic-link traversal, checks the archive listing, and extracts with --no-same-owner.']),
('3.8 Security and Access Control', ['Scripts use set -Eeuo pipefail. monitor.conf is parsed as key/value data and is not sourced as executable shell code. The loader validates numeric thresholds, threshold ordering, report top-N range, filesystem-type syntax, and relative output paths. The restore command checks argument count, archive location, destination syntax, symbolic-link components, and the final resolved destination.', 'The installer attempts mode 750 for project directories and scripts, and mode 640 for configuration, CSV, and logs. Several chmod operations are followed by || true, which can suppress a permission-setting failure; the exact modes were not verified on Ubuntu. Normal monitoring does not require root. Package installation and cron service startup use sudo only when the operator chooses those system-level setup steps. A hostile archive placed in the backup directory is outside the tested threat model; only project-generated archives were used.'])]),
('4. RESULTS AND TESTING', [
('4.1 Implementation Results', ['The project code, configuration, operator instructions, test script, and report-generation components are present. Actual recorded outputs are limited to the Git Bash test transcript: Bash syntax checks passed; alert helper branches wrote the expected test-mount messages; tar archive listing, selected-file recovery, and unsafe-path rejection passed. The final test transcript reports 9 passed, 0 failed, and explicitly skips live df collection, CSV sampling, and report integration on MSYS.', 'There are no genuine Ubuntu terminal screenshots, live capacity values, generated storage_report_*.txt files, installed cron entries, or Linux permission listings in the workspace. These are marked NOT EXECUTED in Table 4.1 and have capture instructions in the evidence appendix.']),
('4.2 Testing and Validation', ['Table 4.1 reports the test case, objective, command, expected result, actual result, and status. “PASS (Git Bash)” identifies a check executed on Windows; it is not an Ubuntu test. Linux-only operations remain NOT EXECUTED. The final text transcript is included in Appendix D and in tests/test_results.txt.'])]),
('5. CONCLUSION AND FUTURE SCOPE', [
('5.1 Conclusion', ['The implementation demonstrates a modular approach to Linux storage administration: capacity and inode collection, configured thresholds, append-only CSV history, log-based alerts, readable reports, scheduled execution, and compressed backup/recovery. The shared configuration and explicit user-level execution keep the toolset small and inspectable. The test evidence supports syntax, alert-helper, and archive/recovery behavior in Git Bash, while the central Ubuntu runtime behavior remains to be demonstrated on the target OS.']),
('5.2 Current Limitations and Future Scope', ['The current release has no email or webhook alert transport, retention policy, charting, daemon, database, or dashboard. CSV fields are emitted as simple comma-separated values rather than a full RFC-compliant quoting routine. Directory-size ranking scans the top level of / and is best-effort; permission errors are discarded. Test coverage skips live collection on MSYS and does not execute cron or permission installation. Future work may add robust CSV escaping, configurable scan roots and retention, tested systemd timer support, alert delivery, trend visualization, and encrypted off-host backups.'])]),
('REFERENCES', [
('Technical References', ['1. GNU Project, GNU Bash Reference Manual, https://www.gnu.org/software/bash/manual/ (accessed 2 November 2026).', '2. GNU Project, GNU Coreutils Manual, sections for df, du, stat, date, sort and tail, https://www.gnu.org/software/coreutils/manual/coreutils.html (accessed 2 November 2026).', '3. GNU Project, GNU Findutils Manual, https://www.gnu.org/software/findutils/manual/find.html (accessed 2 November 2026).', '4. Ubuntu Manpages, crontab(5), https://manpages.ubuntu.com/manpages/jammy/man5/crontab.5.html (accessed 2 November 2026).', '5. Ubuntu Manpages, crontab(1), https://manpages.ubuntu.com/manpages/resolute/man1/crontab.1.html (accessed 2 November 2026).', '6. Linux System Administration Hackathon Based DSA-SEE Guidelines, 09.09.26, pp. 14–15, user-supplied PDF (Project 7 description and evaluation context).', '7. Linux new.pdf, user-supplied 75-page report, used as a structure and presentation reference. No identities, signatures, or approval content are reproduced.'])]),
('APPENDICES', [
('Appendix A. Installation and Execution Commands', ['The exact beginner sequence is provided in documentation/README_Execution_Guide.md. It covers package setup, extracting the transfer ZIP, chmod, installer, run_all.sh, individual modules, cron inspection, report/log inspection, and backup/recovery.']),
('Appendix B. Configuration Example', ['The following values are read from config/monitor.conf. They are data values; the file is not sourced as shell code.']),
('Appendix C. Selected Source Excerpts', ['Listing C.1 shows the actual threshold decision. The alert helper writes the message to both configured logs and stderr.', 'Listing C.2 is the CSV header emitted by init_history().', 'Listing C.3 shows the cron frequencies installed by install_cron.sh.']),
('Appendix D. Recorded Test Transcript', ['The transcript below is taken from tests/test_results.txt. It is compatibility evidence from Git Bash, and the live Linux-only checks were skipped.']),
('Appendix E. Screenshot Evidence Placeholders', ['No terminal screenshot is fabricated. The following figure slots must be replaced with genuine Ubuntu captures after the commands in README_Execution_Guide.md are run. Each caption describes the evidence to collect.'])])]

TEST_ROWS = [
['Test Case','Objective','Command','Expected Result','Actual Result','Status'],
['Source audit','Check report against Project 7 and source','Inspect PDFs and project tree','Report matches selected project and code','Guideline p.15; reference and implementation audited','PASS'],
['Bash syntax','Parse shell modules and tests','bash -n *.sh','No syntax errors','All parser checks passed','PASS (Git Bash)'],
['Threshold bounds','Check 0/100 and reject 101','tests/run_tests.sh','Endpoints accepted; 101 rejected','Regex passed; full config mutation not tested','PASS (limited)'],
['Disk and inode','Collect mounted filesystem capacity','disk_monitor.sh; inode_monitor.sh','Tables and threshold checks','Live collection skipped on MSYS','NOT EXECUTED'],
['CSV / growth','Record repeated samples and delta','storage_growth.sh twice','CSV rows and signed used-byte change','CSV is header-only; live sample skipped','NOT EXECUTED'],
['Alert thresholds','Exercise warning and critical branches','Test helper at 75% / 90%','Both alert levels logged','Expected TEST-MOUNT strings found','PASS (helper)'],
['Run-all and report','Run scan/history/report sequence','run_all.sh; inspect report','Tables, CSV, and report files','Skipped on MSYS; no Linux report output','NOT EXECUTED'],
['Cron','Verify five- and fifteen-minute jobs','install_cron.sh; crontab -l','Marked jobs and cron log entries','No Ubuntu cron evidence','NOT EXECUTED'],
['Backup integrity','Create and list gzip tar','backup_project.sh; tar -tzf','Archive listing succeeds','Final Git Bash test passed','PASS (Git Bash)'],
['Recovery and path safety','Restore files; reject traversal','restore_backup.sh archive destination','README recovered; outside path refused','Both checks passed in Git Bash','PASS (Git Bash)'],
['Permissions / screenshots','Verify modes and collect evidence','stat; capture 12 views','Configured modes and genuine PNG evidence','Neither executed on Ubuntu','NOT EXECUTED'],
]

TREE = '''linux-storage-monitor/\n├── bin/\n│   ├── disk_monitor.sh\n│   ├── inode_monitor.sh\n│   ├── storage_growth.sh\n│   ├── alert_monitor.sh\n│   ├── generate_report.sh\n│   ├── monitor_cycle.sh\n│   ├── run_all.sh\n│   ├── install_cron.sh\n│   ├── backup_project.sh\n│   ├── restore_backup.sh\n│   └── lib/common.sh\n├── config/monitor.conf\n├── data/storage_history.csv  (header only)\n├── logs/  (no live measurements)\n├── reports/  (no runtime report yet)\n├── backup/  (verified test archive and recovery copy)\n├── tests/run_tests.sh, test_results.txt\n├── screenshots/README.md  (capture instructions; no captures yet)\n├── tools/ (documentation generators)\n├── documentation/ (this report and guides)\n├── install.sh / README.md / EXECUTION_GUIDE.md\n└── system_architecture.png'''
CONFIG_TEXT='''WARNING_THRESHOLD=75\nCRITICAL_THRESHOLD=90\nINODE_WARNING_THRESHOLD=75\nINODE_CRITICAL_THRESHOLD=90\nREPORT_TOP_N=10\nEXCLUDED_FILESYSTEM_TYPES=tmpfs,devtmpfs,squashfs,overlay\nALERT_LOG=logs/administrator_alerts.log\nMONITOR_LOG=logs/storage_monitor.log\nHISTORY_CSV=data/storage_history.csv\nREPORT_DIR=reports\nBACKUP_DIR=backup'''
CODE_THRESHOLD='''check_threshold() {\n  local metric=$1 mount=$2 pct=$3 warning=$4 critical=$5\n  if (( pct >= critical )); then alert CRITICAL "$metric" "$mount" "$pct" "$critical"\n  elif (( pct >= warning )); then alert WARNING "$metric" "$mount" "$pct" "$warning"\n  fi\n}'''
CODE_CRON='''*/5 * * * * /path/to/linux-storage-monitor/bin/monitor_cycle.sh >> /path/to/linux-storage-monitor/logs/cron.log 2>&1\n*/15 * * * * /path/to/linux-storage-monitor/bin/generate_report.sh >> /path/to/linux-storage-monitor/logs/cron.log 2>&1'''
CSV_HEADER='timestamp,filesystem,mountpoint,total_bytes,used_bytes,available_bytes,usage_percent,inodes_total,inodes_used,inodes_free,inode_percent'
TRANSCRIPT=(ROOT/'tests/test_results.txt').read_text(encoding='utf-8').strip()

# ReportLab styles and page-numbered contents/list of figures/list of tables.
ss=getSampleStyleSheet()
ss.add(ParagraphStyle(name='BodyA',parent=ss['BodyText'],fontName='Times-Roman',fontSize=10.1,leading=14.3,alignment=TA_JUSTIFY,spaceAfter=7))
ss.add(ParagraphStyle(name='ChapterA',parent=ss['Heading1'],fontName='Times-Bold',fontSize=16,leading=20,alignment=TA_CENTER,textColor=colors.HexColor('#222222'),spaceBefore=4,spaceAfter=12,keepWithNext=True))
ss.add(ParagraphStyle(name='SectionA',parent=ss['Heading2'],fontName='Times-Bold',fontSize=12,leading=15,textColor=colors.HexColor('#222222'),spaceBefore=9,spaceAfter=5,keepWithNext=True))
ss.add(ParagraphStyle(name='SubsectionA',parent=ss['Heading3'],fontName='Times-Bold',fontSize=10.5,leading=13,textColor=colors.HexColor('#333333'),spaceBefore=6,spaceAfter=4,keepWithNext=True))
ss.add(ParagraphStyle(name='CaptionA',parent=ss['BodyText'],fontName='Times-Italic',fontSize=9,leading=11,alignment=TA_CENTER,spaceBefore=3,spaceAfter=9))
ss.add(ParagraphStyle(name='TableCaptionA',parent=ss['BodyText'],fontName='Times-Bold',fontSize=9,leading=11,alignment=TA_CENTER,spaceBefore=5,spaceAfter=5))
ss.add(ParagraphStyle(name='SmallA',parent=ss['BodyText'],fontName='Times-Roman',fontSize=7.4,leading=9.2,spaceAfter=1))
ss.add(ParagraphStyle(name='CodeA',fontName='Courier',fontSize=7.7,leading=9.5,leftIndent=7,rightIndent=7,backColor=colors.HexColor('#f5f5f5'),borderColor=colors.HexColor('#b8b8b8'),borderWidth=.4,borderPadding=6,spaceBefore=4,spaceAfter=7))
ss.add(ParagraphStyle(name='ListA',parent=ss['BodyText'],fontName='Times-Roman',fontSize=9.5,leading=13,leftIndent=14,firstLineIndent=-10,spaceAfter=4))
ss.add(ParagraphStyle(name='CoverA',parent=ss['BodyText'],fontName='Times-Roman',fontSize=12,leading=18,alignment=TA_CENTER,spaceAfter=8))
ss.add(ParagraphStyle(name='CoverTitleA',parent=ss['BodyText'],fontName='Times-Bold',fontSize=17,leading=23,alignment=TA_CENTER,spaceAfter=10))
ss.add(ParagraphStyle(name='TOC1A',fontName='Times-Roman',fontSize=10.2,leading=14,leftIndent=0,firstLineIndent=0,spaceBefore=3))
ss.add(ParagraphStyle(name='TOC2A',fontName='Times-Roman',fontSize=9.3,leading=12,leftIndent=15,firstLineIndent=0))

class FilteredTOC(TableOfContents):
    def __init__(self,accepted,styles): super().__init__(); self.accepted=accepted; self.levelStyles=styles; self.dotsMinLevel=0
    def notify(self,kind,stuff):
        if kind=='TOCEntry':
            level,text,page,key=stuff
            if level in self.accepted: self.addEntry(self.accepted[level],text,page,key)

class AcademicDoc(SimpleDocTemplate):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        self.entry_pages={}
    def afterFlowable(self,flowable):
        if isinstance(flowable,Paragraph) and getattr(flowable,'_entry',None):
            level,text,key=flowable._entry
            self.entry_pages[key]=self.page
            self.canv.bookmarkPage(key)
            if level in (0,1): self.canv.addOutlineEntry(text,key,level=level,closed=(level==0))
            self.notify('TOCEntry',(level,text,self.page,key))

def esc(s): return str(s).replace('&','&amp;').replace('<','&lt;').replace('>','&gt;')
def heading(text,style,level,key):
    p=Paragraph(esc(text),style); p._entry=(level,text,key); return p
def listed_table(rows,widths,font=7.5,header=True):
    data=[[Paragraph(esc(c),ss['SmallA']) for c in row] for row in rows]
    t=Table(data,colWidths=widths,repeatRows=1 if header else 0,hAlign='CENTER')
    commands=[('GRID',(0,0),(-1,-1),.35,colors.HexColor('#6b6b6b')),('VALIGN',(0,0),(-1,-1),'TOP'),('LEFTPADDING',(0,0),(-1,-1),4),('RIGHTPADDING',(0,0),(-1,-1),4),('TOPPADDING',(0,0),(-1,-1),4),('BOTTOMPADDING',(0,0),(-1,-1),4),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#fafafa')])]
    if header: commands += [('BACKGROUND',(0,0),(-1,0),colors.HexColor('#eeeeee')),('FONTNAME',(0,0),(-1,0),'Times-Bold')]
    t.setStyle(TableStyle(commands)); return t

story=[]
# Cover styled after the reference's white, framed, centered academic cover.
story += [Spacer(1,15*mm),Paragraph(' [INSTITUTION / UNIVERSITY NAME] ',ss['CoverA']),Spacer(1,12*mm),Paragraph('[DEPARTMENT NAME]',ss['CoverA']),Spacer(1,8*mm),Paragraph('[COURSE NAME] ([COURSE CODE])',ss['CoverA']),Spacer(1,6*mm),Paragraph('LINUX INFRASTRUCTURE DEPLOYMENT PROJECT REPORT',ss['CoverTitleA']),Spacer(1,4*mm),Paragraph('On',ss['CoverA']),Paragraph('LINUX STORAGE MONITORING SYSTEM',ss['CoverTitleA']),Spacer(1,4*mm),Paragraph('Submitted by',ss['CoverA']),Paragraph('[STUDENT NAME(S)]<br/>[REGISTER NUMBER(S)]',ss['CoverA']),Spacer(1,5*mm),Paragraph('In partial fulfilment of the academic requirements for<br/>[PROGRAMME / DEGREE / SPECIALIZATION]',ss['CoverA']),Spacer(1,5*mm),Paragraph('Under the supervision of<br/>[FACULTY SUPERVISOR NAME / DESIGNATION]',ss['CoverA']),Spacer(1,8*mm),Paragraph('[ACADEMIC YEAR]<br/>[SUBMISSION DATE]',ss['CoverA']),PageBreak()]
# A certificate template, explicitly not a fabricated approval.
story += [Spacer(1,12*mm),Paragraph('[DEPARTMENT NAME]',ss['CoverA']),Paragraph('[INSTITUTION / UNIVERSITY NAME]',ss['CoverA']),Spacer(1,15*mm),Paragraph('CERTIFICATE TEMPLATE — NOT AN APPROVAL',ss['CoverTitleA']),Spacer(1,10*mm),Paragraph('This page is an editable certificate template only. The authorized faculty and institution must replace the bracketed fields and confirm the project after review. No approval, signature, or certification is asserted by this document.',ss['BodyA']),Spacer(1,12*mm),Paragraph('Project title: <b>Linux Storage Monitoring System</b>',ss['BodyA']),Paragraph('Student name(s): [TO BE COMPLETED]',ss['BodyA']),Paragraph('Register number(s): [TO BE COMPLETED]',ss['BodyA']),Paragraph('Course and academic year: [TO BE COMPLETED]',ss['BodyA']),Spacer(1,25*mm),Paragraph('Authorized faculty supervisor: [NAME / DESIGNATION]\nSignature and date: [TO BE COMPLETED BY AUTHORIZED FACULTY]',ss['CoverA']),Spacer(1,12*mm),Paragraph('Course coordinator / department authority: [OPTIONAL INSTITUTIONAL FIELD]\nSignature and date: [TO BE COMPLETED BY AUTHORIZED PERSON]',ss['CoverA']),PageBreak()]
story += [heading('TABLE OF CONTENTS',ss['ChapterA'],None,'toc-title'),FilteredTOC({0:0,1:1},[ss['TOC1A'],ss['TOC2A']]),PageBreak(),heading('LIST OF FIGURES',ss['ChapterA'],None,'fig-title'),FilteredTOC({2:0},[ss['TOC1A']]),PageBreak(),heading('LIST OF TABLES',ss['ChapterA'],None,'table-title'),FilteredTOC({3:0},[ss['TOC1A']]),PageBreak()]

def add_caption(text,kind,key):
    p=Paragraph(esc(text),ss['CaptionA'] if kind==2 else ss['TableCaptionA']); p._entry=(kind,text,key); story.append(p)
def add_paragraphs(blocks):
    for text in blocks: story.append(Paragraph(esc(text),ss['BodyA']))
for cidx,(chapter,sections) in enumerate(CHAPTERS,1):
    if cidx>1: story.append(PageBreak())
    story.append(heading(chapter,ss['ChapterA'],0,f'ch{cidx}'))
    for sidx,(sec,paras) in enumerate(sections,1):
        style=ss['SectionA']
        story.append(heading(sec,style,1,f'ch{cidx}s{sidx}'))
        add_paragraphs(paras)
        if sec.startswith('2.1.1'):
            rows=[['Utility','Observed use in project'],['bash','Module language, strict mode, control flow, arithmetic, and arrays'],['df','Block capacity and inode usage; used by monitoring and report commands'],['stat','Filesystem type for configured exclusion filtering'],['awk','Lookup of previous mountpoint usage in CSV history'],['du / sort / tail','Best-effort top-level size ranking in generated report'],['date / tee / touch / mkdir','Timestamps, append/display logging, file and directory initialization'],['find / chmod / ls','Installer file modes; ls is used in test/operator commands'],['grep / crontab / mktemp','Marked cron line replacement in the cron installer'],['tar / gzip / realpath','Backup archive, archive listing, resolved-path restrictions, recovery'],['sed','Installed by package guidance but not invoked by the project scripts']]
            add_caption('Table 2.1: Utilities used by the implementation',3,'tab21'); story.append(listed_table(rows,[38*mm,135*mm]));
        if sec.startswith('3.1'):
            story.append(Image(str(ARCH),width=172*mm,height=113*mm)); add_caption('Figure 3.1: System architecture derived from the inspected implementation',2,'fig31')
        if sec.startswith('3.4'):
            story.append(Preformatted(TREE,ss['CodeA'])); add_caption('Figure 3.2: Audited project directory structure',2,'fig32')
            rows=[['Path','Purpose / present state'],['bin/','Bash modules and shared library'],['config/monitor.conf','Thresholds, exclusions, and relative output locations'],['data/storage_history.csv','Header exists; no Ubuntu samples yet'],['logs/','Runtime monitor and alert logs; no live readings retained'],['reports/','Empty until generate_report.sh runs on target Linux'],['backup/','Git Bash test archive and restored project copy'],['tests/','Integration test source and actual test transcript'],['screenshots/','Instructions only; no captures collected'],['documentation/','Final report and companion guides']]
            add_caption('Table 3.1: Project directory and file roles',3,'tab31'); story.append(listed_table(rows,[48*mm,125*mm]));
        if sec.startswith('3.6'):
            story.append(Preformatted('df -P -B1     # bytes: total, used, available, percentage\ndf -P -i       # inode totals, use, free count, percentage\nstat -f -c %T -- "$mount"   # filesystem type used for exclusions',ss['CodeA']))
        if sec.startswith('3.7'):
            story.append(Preformatted(CSV_HEADER,ss['CodeA']))
            story.append(Preformatted(CODE_CRON,ss['CodeA']))
        if sec.startswith('3.8'):
            story.append(Preformatted(CODE_THRESHOLD,ss['CodeA']))
        if sec.startswith('4.2'):
            story.append(Spacer(1,3*mm)); add_caption('Table 4.1: Test and validation results',3,'tab41')
            story.append(listed_table(TEST_ROWS,[20*mm,26*mm,28*mm,29*mm,43*mm,24*mm]))
        if sec.startswith('Appendix B'):
            story.append(Preformatted(CONFIG_TEXT,ss['CodeA']))
        if sec.startswith('Appendix C'):
            for label,code in [('Listing C.1: Threshold decision function',CODE_THRESHOLD),('Listing C.2: CSV schema',CSV_HEADER),('Listing C.3: Cron schedule template',CODE_CRON)]:
                story.append(Paragraph(esc(label),ss['SubsectionA'])); story.append(Preformatted(code,ss['CodeA']))
        if sec.startswith('Appendix D'):
            story.append(Preformatted(TRANSCRIPT,ss['CodeA']))
        if sec.startswith('Appendix E'):
            for i,label in enumerate(FIGURES[2:],1):
                # A numbered, white placeholder panel: it cannot be mistaken for evidence.
                panel=Table([[Paragraph('<b>SCREENSHOT PLACEHOLDER — NOT CAPTURED</b><br/><br/>Insert a genuine Ubuntu terminal capture for this figure. See README_Execution_Guide.md for the exact command.',ss['SmallA'])]],colWidths=[170*mm],rowHeights=[28*mm])
                panel.setStyle(TableStyle([('BOX',(0,0),(-1,-1),.8,colors.HexColor('#777777')),('BACKGROUND',(0,0),(-1,-1),colors.white),('ALIGN',(0,0),(-1,-1),'CENTER'),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('LEFTPADDING',(0,0),(-1,-1),8),('RIGHTPADDING',(0,0),(-1,-1),8)]))
                story.append(KeepTogether([panel])); add_caption(f'Figure 4.{i}: {label}',2,f'fig4{i}')

def page_chrome(canvas,doc):
    canvas.saveState(); w,h=A4
    # Fine double rule follows the reference's light academic page frame.
    canvas.setStrokeColor(colors.HexColor('#555555')); canvas.setLineWidth(.45)
    canvas.rect(10*mm,10*mm,w-20*mm,h-20*mm)
    canvas.setLineWidth(.25); canvas.rect(11.2*mm,11.2*mm,w-22.4*mm,h-22.4*mm)
    if doc.page>1:
        canvas.setFont('Times-Roman',8.5); canvas.setFillColor(colors.HexColor('#333333'))
        canvas.drawString(18*mm,h-14*mm,'Linux System Administration')
        canvas.drawRightString(w-18*mm,h-14*mm,'[COURSE CODE]')
        canvas.drawRightString(w-18*mm,14*mm,str(doc.page))
    canvas.restoreState()

pdf=AcademicDoc(str(PDF_PATH),pagesize=A4,rightMargin=19*mm,leftMargin=19*mm,topMargin=20*mm,bottomMargin=20*mm,title='Linux Storage Monitoring System',author='[STUDENT NAME]')
pdf.multiBuild(story)
PAGE_BY_KEY=pdf.entry_pages

# DOCX uses the same content and a similar white, serif academic layout.
def shade(cell,fill='EEEEEE'):
    shd=OxmlElement('w:shd'); shd.set(qn('w:fill'),fill); cell._tc.get_or_add_tcPr().append(shd)
def set_cell_text(cell,text,bold=False,size=8.2):
    cell.text=''; cell.vertical_alignment=WD_CELL_VERTICAL_ALIGNMENT.TOP
    p=cell.paragraphs[0]; p.paragraph_format.space_after=Pt(1)
    r=p.add_run(str(text)); r.bold=bold; r.font.name='Times New Roman'; r.font.size=Pt(size); r.font.color.rgb=RGBColor(40,40,40)
def doc_table(doc,rows,widths):
    t=doc.add_table(rows=0,cols=len(rows[0])); t.style='Table Grid'; t.alignment=WD_TABLE_ALIGNMENT.CENTER
    for ri,row in enumerate(rows):
        cells=t.add_row().cells
        for j,val in enumerate(row):
            set_cell_text(cells[j],val,bold=ri==0,size=7.4 if len(row)>4 else 8.4)
            if ri==0: shade(cells[j])
        trPr=t.rows[-1]._tr.get_or_add_trPr(); trPr.append(OxmlElement('w:cantSplit'))
        if ri==0:
            repeat=OxmlElement('w:tblHeader'); repeat.set(qn('w:val'),'true'); trPr.append(repeat)
    for row in t.rows:
        for cell,w in zip(row.cells,widths): cell.width=Inches(w)
    return t
def add_field(paragraph,instruction,placeholder=''):
    r=paragraph.add_run(); begin=OxmlElement('w:fldChar'); begin.set(qn('w:fldCharType'),'begin'); r._r.append(begin)
    r=paragraph.add_run(); ins=OxmlElement('w:instrText'); ins.set(qn('xml:space'),'preserve'); ins.text=instruction; r._r.append(ins)
    r=paragraph.add_run(); sep=OxmlElement('w:fldChar'); sep.set(qn('w:fldCharType'),'separate'); r._r.append(sep)
    if placeholder:
        r=paragraph.add_run(placeholder); r.font.name='Times New Roman'; r.font.size=Pt(9)
    r=paragraph.add_run(); end=OxmlElement('w:fldChar'); end.set(qn('w:fldCharType'),'end'); r._r.append(end)

doc=Document(); sec=doc.sections[0]; sec.page_width=Inches(8.27); sec.page_height=Inches(11.69); sec.top_margin=Inches(.78); sec.bottom_margin=Inches(.75); sec.left_margin=Inches(.85); sec.right_margin=Inches(.85)
for name in ['Normal','Title','Subtitle','Heading 1','Heading 2','Heading 3']:
    st=doc.styles[name]; st.font.name='Times New Roman'; st.font.color.rgb=RGBColor(35,35,35)
doc.styles['Normal'].font.size=Pt(10.5); doc.styles['Normal'].paragraph_format.space_after=Pt(6); doc.styles['Normal'].paragraph_format.line_spacing=1.12
doc.styles['Heading 1'].font.size=Pt(16); doc.styles['Heading 1'].font.bold=True
doc.styles['Heading 2'].font.size=Pt(12); doc.styles['Heading 2'].font.bold=True
doc.styles['Heading 3'].font.size=Pt(10.5); doc.styles['Heading 3'].font.bold=True
# Double frame, white page throughout.
sectPr=sec._sectPr; borders=OxmlElement('w:pgBorders'); borders.set(qn('w:offsetFrom'),'page')
for edge in ('top','left','bottom','right'):
    el=OxmlElement('w:'+edge); el.set(qn('w:val'),'double'); el.set(qn('w:sz'),'4'); el.set(qn('w:space'),'15'); el.set(qn('w:color'),'777777'); borders.append(el)
sectPr.append(borders)
header=sec.header.paragraphs[0]; header.text='Linux System Administration'; header.alignment=WD_ALIGN_PARAGRAPH.LEFT
hr=header.add_run(' '*68+'[COURSE CODE]'); hr.font.name='Times New Roman'; hr.font.size=Pt(8)
footer=sec.footer.paragraphs[0]; footer.alignment=WD_ALIGN_PARAGRAPH.RIGHT; add_field(footer,'PAGE','1')
settings=doc.settings._element; update=OxmlElement('w:updateFields'); update.set(qn('w:val'),'true'); settings.append(update)

def center(text,bold=False,size=12):
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.space_after=Pt(10)
    r=p.add_run(text); r.bold=bold; r.font.name='Times New Roman'; r.font.size=Pt(size); return p
center('[INSTITUTION / UNIVERSITY NAME]',False,12); center('[DEPARTMENT NAME]'); center('[COURSE NAME] ([COURSE CODE])')
for _ in range(2): doc.add_paragraph()
center('LINUX INFRASTRUCTURE DEPLOYMENT PROJECT REPORT',True,17); center('On'); center('LINUX STORAGE MONITORING SYSTEM',True,18)
for _ in range(2): doc.add_paragraph()
center('Submitted by'); center('[STUDENT NAME(S)]\n[REGISTER NUMBER(S)]'); center('In partial fulfilment of the academic requirements for\n[PROGRAMME / DEGREE / SPECIALIZATION]'); center('Under the supervision of\n[FACULTY SUPERVISOR NAME / DESIGNATION]')
for _ in range(2): doc.add_paragraph()
center('[ACADEMIC YEAR]\n[SUBMISSION DATE]'); doc.add_page_break()
center('[DEPARTMENT NAME]'); center('[INSTITUTION / UNIVERSITY NAME]'); doc.add_paragraph(); center('CERTIFICATE TEMPLATE — NOT AN APPROVAL',True,16)
doc.add_paragraph('This page is an editable certificate template only. The authorized faculty and institution must replace the bracketed fields and confirm the project after review. No approval, signature, or certification is asserted by this document.')
doc.add_paragraph('Project title: Linux Storage Monitoring System\nStudent name(s): [TO BE COMPLETED]\nRegister number(s): [TO BE COMPLETED]\nCourse and academic year: [TO BE COMPLETED]')
for _ in range(5): doc.add_paragraph()
center('Authorized faculty supervisor: [NAME / DESIGNATION]\nSignature and date: [TO BE COMPLETED BY AUTHORIZED FACULTY]')
center('Course coordinator / department authority: [OPTIONAL INSTITUTIONAL FIELD]\nSignature and date: [TO BE COMPLETED BY AUTHORIZED PERSON]'); doc.add_page_break()
for title,field in [('TABLE OF CONTENTS','TOC \\o "1-2" \\h \\z \\u'),('LIST OF FIGURES','TOC \\h \\c "Figure"'),('LIST OF TABLES','TOC \\h \\c "Table"')]:
    doc.add_heading(title,0)
    p=doc.add_paragraph(); add_field(p,field,'Update this field in Word (Ctrl+A, F9).')
    doc.add_page_break()

def doc_caption(text, label):
    p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
    r=p.add_run(text); r.font.name='Times New Roman'; r.font.size=Pt(9)
    add_field(p, f'SEQ {label} \\* ARABIC', '1')
    for run in p.runs:
        if run.text == '1': run.font.hidden = True
    return p

for cidx,(chapter,sections) in enumerate(CHAPTERS,1):
    if cidx>1: doc.add_page_break()
    doc.add_heading(chapter,1)
    for sidx,(secname,paras) in enumerate(sections,1):
        doc.add_heading(secname,2)
        for para in paras: doc.add_paragraph(para)
        if secname.startswith('2.1.1'):
            doc_caption('Table 2.1: Utilities used by the implementation','Table')
            doc_table(doc,[['Utility','Observed use in project'],['bash','Module language, strict mode, control flow, arithmetic, and arrays'],['df','Block capacity and inode usage'],['stat','Filesystem type filtering'],['awk','Previous CSV sample lookup'],['du / sort / tail','Best-effort directory-size ranking'],['date / tee / touch / mkdir','Timestamps, logs, and file setup'],['find / chmod','Installer permission operation'],['grep / crontab / mktemp','Marked cron replacement'],['tar / gzip / realpath','Backup, verification, and safe recovery'],['sed','Guidance dependency; not called by project scripts']],[1.4,5.25])
        if secname.startswith('3.1'):
            p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER; p.add_run().add_picture(str(ARCH),width=Inches(6.35)); doc_caption('Figure 3.1: System architecture derived from inspected implementation','Figure')
        if secname.startswith('3.4'):
            p=doc.add_paragraph(); r=p.add_run(TREE); r.font.name='Consolas'; r.font.size=Pt(8)
            doc_caption('Figure 3.2: Audited project directory structure','Figure')
            doc_caption('Table 3.1: Project directory and file roles','Table')
            doc_table(doc,[['Path','Purpose / present state'],['bin/','Bash modules and shared library'],['config/monitor.conf','Thresholds, exclusions, and relative output locations'],['data/storage_history.csv','Header exists; no Ubuntu samples yet'],['logs/','Runtime monitor and alert logs; no live readings retained'],['reports/','Empty until generate_report.sh runs on target Linux'],['backup/','Git Bash test archive and restored project copy'],['tests/','Integration test source and actual transcript'],['screenshots/','Instructions only; no captures yet'],['documentation/','Final reports and companion guides']],[1.65,5.0])
        if secname.startswith('3.6'):
            p=doc.add_paragraph(); r=p.add_run('df -P -B1     # byte capacity\ndf -P -i       # inode usage\nstat -f -c %T -- "$mount"   # filesystem type'); r.font.name='Consolas'; r.font.size=Pt(9)
        if secname.startswith('3.7'):
            p=doc.add_paragraph(); r=p.add_run(CSV_HEADER); r.font.name='Consolas'; r.font.size=Pt(7.5)
            p=doc.add_paragraph(); r=p.add_run(CODE_CRON); r.font.name='Consolas'; r.font.size=Pt(8)
        if secname.startswith('3.8'):
            p=doc.add_paragraph(); r=p.add_run(CODE_THRESHOLD); r.font.name='Consolas'; r.font.size=Pt(8)
        if secname.startswith('4.2'):
            doc_caption('Table 4.1: Test and validation results','Table')
            doc_table(doc,TEST_ROWS,[.92,1.15,1.23,1.08,1.52,.5])
        if secname.startswith('Appendix B'):
            p=doc.add_paragraph(); r=p.add_run(CONFIG_TEXT); r.font.name='Consolas'; r.font.size=Pt(9)
        if secname.startswith('Appendix C'):
            for label,code in [('Listing C.1: Threshold decision function',CODE_THRESHOLD),('Listing C.2: CSV schema',CSV_HEADER),('Listing C.3: Cron schedule template',CODE_CRON)]:
                doc.add_heading(label,3); p=doc.add_paragraph(); r=p.add_run(code); r.font.name='Consolas'; r.font.size=Pt(8)
        if secname.startswith('Appendix D'):
            p=doc.add_paragraph(); r=p.add_run(TRANSCRIPT); r.font.name='Consolas'; r.font.size=Pt(8)
        if secname.startswith('Appendix E'):
            doc.add_page_break()
            for i,label in enumerate(FIGURES[2:],1):
                t=doc.add_table(rows=1,cols=1); t.style='Table Grid'; c=t.cell(0,0); c.height=Inches(.9); c.text='SCREENSHOT PLACEHOLDER — NOT CAPTURED\nInsert genuine Ubuntu terminal evidence for this figure. See README_Execution_Guide.md.'
                shade(c,'FFFFFF'); doc_caption(f'Figure 4.{i}: {label}','Figure')
doc.save(DOCX_PATH)

# Companion guide focuses on exact operator actions; test protocol is separately auditable.
guide='''# README — Execution Guide\n\n## Scope and host status\n\nThis project targets Ubuntu Linux (Ubuntu 20.04 or newer is recommended). The authored workspace was Windows/MSYS. WSL was unavailable, so live Linux collection, report generation, cron timing, and Ubuntu permissions still require execution on the target machine. The ZIP should be copied to `~/Downloads` on Ubuntu.\n\n## Install and start\n\n```bash\nsudo apt update\nsudo apt install -y bash coreutils findutils gawk sed grep tar gzip cron unzip\nunzip ~/Downloads/linux-storage-monitor.zip -d "$HOME"\ncd "$HOME/linux-storage-monitor"\nchmod +x install.sh bin/*.sh bin/lib/*.sh tests/*.sh\n./install.sh\n./bin/run_all.sh\n```\n\nThe installer checks `/etc/os-release`, checks command presence, creates runtime directories and the CSV header, and attempts mode 750 for scripts/directories and 640 for config/data/logs. It prints package guidance if utilities are missing; it does not install packages. Inspect the mode results with `stat -c '%a %n' ...`. The installer's `chmod ... || true` clauses can hide failures, so check each result.\n\n## Run modules\n\n```bash\n./bin/disk_monitor.sh\n./bin/inode_monitor.sh\n./bin/storage_growth.sh\n./bin/alert_monitor.sh\n./bin/generate_report.sh\n./tests/run_tests.sh\n```\n\nEdit `config/monitor.conf` to change block/inode warning and critical percentages. Values must be integer 0–100; each warning must remain below its critical threshold. `run_all.sh` performs disk, inode, CSV growth, and text report work in sequence.\n\n## Inspect files\n\n```bash\ncolumn -s, -t < data/storage_history.csv | tail -n 15\ntail -n 50 logs/administrator_alerts.log\ntail -n 50 logs/storage_monitor.log\nls -lh reports/\ncat reports/storage_report_*.txt\nfind . -maxdepth 3 -type f -print | sort\n```\n\nCSV has one row per included mountpoint per sample. The first sample is a baseline; later rows print the change in used bytes since the previous sample.\n\n## Cron: 5-minute monitoring / 15-minute report\n\n```bash\nsudo systemctl enable --now cron\n./bin/install_cron.sh\ncrontab -l\nsystemctl status cron --no-pager\ntail -f logs/cron.log\n```\n\nThe monitor cycle collects disk/inode data and appends growth history every five minutes. Report generation runs every fifteen minutes. Cron commands run under the current user's account. The installer preserves unrelated entries and replaces only lines tagged `LINUX_STORAGE_MONITOR`. Wait for at least one matching interval before treating this as runtime-verified.\n\n## Backup and recovery\n\n```bash\n./bin/backup_project.sh\narchive=$(ls -1t backup/linux-storage-monitor_*.tar.gz | head -n 1)\ntar -tzf "$archive" | head\nmkdir -p backup/demo-recovery\n./bin/restore_backup.sh "$archive" backup/demo-recovery\nfind backup/demo-recovery -maxdepth 2 -type f -print\n```\n\nThe archive covers scripts, configuration, data, tests, documentation sources, guides, and architecture image. It is listed with `tar -tzf` before success is reported. Recovery requires an archive under the configured backup directory and a destination below `backup/`; parent traversal and symbolic-link path components are rejected.\n\n## Faculty demonstration and evidence screenshots\n\nCapture these twelve genuine terminal views in `screenshots/` and caption them as Figures 4.1–4.12 in the report. Use Ubuntu Terminal and crop away unrelated desktop content.\n\n1. Environment: `uname -a; cat /etc/os-release`\n2. Tree: `find . -maxdepth 3 -type f -print | sort`\n3. Installation: show the completed `./install.sh` output (also show apt package command if required).\n4. Disk: `./bin/disk_monitor.sh`\n5. Inodes: `./bin/inode_monitor.sh`\n6. Growth: `./bin/storage_growth.sh; tail -n 8 data/storage_history.csv`\n7. Alert: save config, temporarily lower a warning threshold below observed use, run the corresponding monitor, then restore config: `cp config/monitor.conf /tmp/monitor.conf.saved`; edit with `nano`; run module; `cp /tmp/monitor.conf.saved config/monitor.conf`. Do not fill a filesystem.\n8. Report: `./bin/generate_report.sh; latest=$(ls -1t reports/*.txt | head -1); head -n 45 "$latest"`\n9. Cron: `crontab -l; tail -n 20 logs/cron.log` after jobs have fired.\n10. Backup creation: `./bin/backup_project.sh; ls -lh backup/*.tar.gz`\n11. Integrity: `tar -tzf "$archive" | head`\n12. Recovery: `./bin/restore_backup.sh "$archive" backup/demo-recovery; find backup/demo-recovery -maxdepth 2 -type f -print`\n\nNo screenshot is embedded as if captured. Run `./tests/run_tests.sh` and retain its actual transcript. Then update DOCX fields (Ctrl+A, F9 in Word), check page numbers after the fields refresh, fill placeholders, and export a reviewed PDF if pagination changes.\n'''
(OUT/'README_Execution_Guide.md').write_text(guide,encoding='utf-8')

test_doc='''# Testing and Validation\n\n## Environment and evidence boundary\n\nTest transcript: `../tests/test_results.txt`. The final run used Git for Windows Bash and reported **9 passed, 0 failed**. It skipped the live disk/inode, CSV sampling, and runtime report integration because the host identified as `MSYS_NT-10.0-26200`. WSL had returned access denied. Thus Git Bash checks are not claimed as Ubuntu execution. The saved transcript is the source of actual pass/skip results.\n\n## Test results\n\n| Test Case | Objective | Command | Expected Result | Actual Result | Status |\n|---|---|---|---|---|---|\n| Reference and source audit | Ensure report matches Project 7 and current files | Inspect both supplied PDFs and project files | Project selection and report claims reflect source | Project 7 found on guideline p. 15; 75-page reference reviewed; all modules/config/tests inspected | PASS (audit) |\n| Bash syntax | Parse executable scripts | `bash -n` for install, modules, library, tests | No syntax errors | Parser checks passed in Git Bash | PASS (Git Bash) |\n| Threshold expression bounds | Check 0/100 accepted and 101 rejected | `./tests/run_tests.sh` | Endpoints pass; 101 rejected | Transcript checks passed; this tests the regex expression, not full config file mutation | PASS (limited) |\n| Disk monitoring | Read per-filesystem byte capacity | `./bin/disk_monitor.sh` | Filesystem table and threshold handling | Live Linux collection skipped on MSYS; not executed on Ubuntu | NOT EXECUTED |\n| Inode monitoring | Read per-filesystem inode counts | `./bin/inode_monitor.sh` | Inode table and threshold handling | Live Linux collection skipped on MSYS; not executed on Ubuntu | NOT EXECUTED |\n| CSV and growth delta | Record repeated timestamped samples | `./bin/storage_growth.sh` twice | Header, rows, prior-sample delta | CSV remains header-only; live sample skipped | NOT EXECUTED |\n| Warning / critical helper | Exercise both alert branches without storage pressure | `check_threshold` helper calls in test script | Test warning and critical lines in alert log | Both expected TEST-MOUNT messages were found | PASS (helper only) |\n| Complete cycle / report | Run all modules and create text report | `./bin/run_all.sh` | Tables, CSV sample, timestamped report | Live Linux cycle skipped; Windows drive labels with spaces caused a direct MSYS run to be incompatible | NOT EXECUTED on Ubuntu |\n| Report contents | Verify df, du, alerts, history sections | `./bin/generate_report.sh` | Readable timestamped report | No runtime report generated from Linux data | NOT EXECUTED |\n| Cron setup/timing | Verify per-user schedule at 5 and 15 minutes | `sudo systemctl enable --now cron; ./bin/install_cron.sh; crontab -l` | Marked entries and cron log activity | No Ubuntu cron service or schedule evidence | NOT EXECUTED |\n| Backup integrity | Create and inspect compressed archive | `./bin/backup_project.sh; tar -tzf "$archive"` | Archive listing succeeds | Final Git Bash test passed archive check | PASS (Git Bash) |\n| Recovery | Extract selected files to isolated project directory | `./bin/restore_backup.sh "$archive" backup/test-recovery` | Recovered README exists | Test transcript reports selected-file recovery passed | PASS (Git Bash) |\n| Traversal rejection | Reject parent-directory target | `./bin/restore_backup.sh "$archive" ../outside` | Nonzero result; no external write | Test rejection check passed | PASS (Git Bash) |\n| Permissions | Verify 750/640 modes on target filesystem | `./install.sh; stat -c '%a %n' ...` | Script and data modes as configured | Installer chmod not executed on Ubuntu; errors can be suppressed by `|| true` | NOT EXECUTED |\n| Screenshot evidence | Capture genuine implementation output | Commands in README_Execution_Guide.md | 12 readable PNGs with captions | No Linux screenshots in workspace; placeholder slots only | NOT EXECUTED |\n\n## Saved final test transcript\n\n```text\n'''+TRANSCRIPT+'''\n```\n\n## Manual Ubuntu verification protocol\n\n1. Run `./install.sh`, then inspect its exit status and verify 750/640 modes with `stat`.\n2. Run disk and inode modules and save their unedited output.\n3. Run storage_growth.sh twice; confirm CSV row counts and compare the used-byte delta.\n4. Trigger threshold branches only by temporarily lowering a threshold below existing usage; restore config immediately. Never consume disk space for a demonstration.\n5. Generate a text report and inspect all sections.\n6. Install cron, preserve the output of `crontab -l`, wait at least 15 minutes, then inspect `logs/cron.log` and Ubuntu syslog.\n7. Create a new archive, run `tar -tzf`, recover to `backup/demo-recovery`, and compare a recovered file with its source using `diff`.\n8. Capture and insert the twelve screenshots listed in the guide.\n\nAll unexecuted checks should remain marked NOT EXECUTED until their actual Ubuntu output is recorded.\n'''
(OUT/'Testing_and_Validation.md').write_text(test_doc,encoding='utf-8')

print(DOCX_PATH); print(PDF_PATH); print(OUT/'README_Execution_Guide.md'); print(OUT/'Testing_and_Validation.md')
