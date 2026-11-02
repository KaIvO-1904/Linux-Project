#!/usr/bin/env python3
"""Generate editable DOCX and PDF academic reports for the actual project."""
from pathlib import Path
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, Image, Preformatted
from PIL import Image as PILImage, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parents[1]
DOCX_OUT = ROOT / 'Linux_Storage_Monitoring_System_Report.docx'
PDF_OUT = ROOT / 'Linux_Storage_Monitoring_System_Report.pdf'
SHOT = ROOT / 'screenshots'
SHOT.mkdir(exist_ok=True)
TREE = '''linux-storage-monitor/\n├── bin/ (modules)\n│   └── lib/common.sh\n├── config/monitor.conf\n├── data/storage_history.csv\n├── logs/ (monitor, alert, cron)\n├── reports/\n├── backup/\n├── tests/run_tests.sh\n├── screenshots/README.md\n├── tools/build_report.py\n├── install.sh\n├── README.md\n└── EXECUTION_GUIDE.md'''

def make_architecture():
    im=PILImage.new('RGB',(1500,850),'#f4f7fb'); d=ImageDraw.Draw(im)
    fp='C:/Windows/Fonts/arial.ttf'; title=ImageFont.truetype(fp,38); body=ImageFont.truetype(fp,27); small=ImageFont.truetype(fp,21)
    d.text((750,35),'Linux Storage Monitoring System — Architecture',fill='#14243a',font=title,anchor='mt')
    def box(x,y,w,h,head,lines):
        d.rounded_rectangle((x,y,x+w,y+h),18,fill='white',outline='#3a628c',width=3)
        d.text((x+w//2,y+16),head,fill='#17385e',font=body,anchor='mt')
        for i,line in enumerate(lines): d.text((x+16,y+62+i*31),line,fill='#26384b',font=small)
    def arrow(a,b):
        import math
        d.line((a,b),fill='#345b80',width=5); ang=math.atan2(b[1]-a[1],b[0]-a[0]); L=18
        d.polygon((b,(b[0]-L*math.cos(ang-.5),b[1]-L*math.sin(ang-.5)),(b[0]-L*math.cos(ang+.5),b[1]-L*math.sin(ang+.5))),fill='#345b80')
    box(65,150,330,200,'Ubuntu filesystems',['Mounted volumes','Blocks + inode counters'])
    box(570,115,370,260,'Bash collectors',['disk_monitor.sh','inode_monitor.sh','storage_growth.sh'])
    box(1120,100,310,150,'Threshold alerts',['Warning / critical','administrator_alerts.log'])
    box(1120,310,310,150,'CSV history',['storage_history.csv','timestamp + deltas'])
    box(570,500,370,210,'Reports + backup',['generate_report.sh','tar.gz + integrity check'])
    box(65,520,330,160,'Cron scheduler',['5 min monitor cycle','15 min report job'])
    arrow((395,245),(570,245)); arrow((940,205),(1120,175)); arrow((940,300),(1120,380)); arrow((755,375),(755,500)); arrow((395,600),(570,610))
    path=ROOT/'system_architecture.png'; im.save(path); return path

ARCH=make_architecture()
chapters=[
('1. Introduction',[
('1.1 Aim','Develop a lightweight Bash system that observes Linux filesystem capacity and inode use, tracks changes, warns administrators at configured limits, and produces readable reports.'),
('1.2 Background','A filesystem can exhaust data blocks or inodes. Either condition can stop applications from creating files. Manual df checks provide only a momentary view; scripts and cron can preserve history and make checks routine.'),
('1.3 Problem Statement','Administrators need timely visibility into disk use, inode use, and capacity trends. The solution must collect observations, compare percentages with thresholds, retain timestamped history, log alerts, and support inspection and recovery.'),
('1.4 Objectives','Monitor filesystems; record CSV samples and growth deltas; warn at configurable warning and critical thresholds; generate timestamped reports; schedule checks with cron; create verified compressed backups; and recover selected project files safely.')]),
('2. Methodology',[
('2.1 Tools and Technologies Used','Ubuntu Linux, Bash, GNU df, du, stat, awk, sed, grep, date, tar, gzip, cron, sort, and tail. Python 3, python-docx, ReportLab, and Pillow build the academic deliverables only.'),
('2.2 Hardware and Software Requirements','An Ubuntu desktop/server, regular user account, Bash, GNU utilities, findutils, awk, sed, grep, tar, gzip, and cron. Package installation requires sudo; ordinary monitoring does not.'),
('2.3 Approach / Development Process','The project separates configuration, scripts, data, logs, reports, backups, tests, and screenshots. A common Bash library validates configuration and centralizes alerts. Individual scripts support inspection; run_all.sh gives a single complete cycle. Cron separates five-minute scans from fifteen-minute reports. Tests use existing system data and small archives.')]),
('3. Linux System Administration – Design and Implementation',[
('3.1 System Architecture','Collectors obtain mounted-filesystem statistics with standard utilities. The common library validates configuration, records alerts, and supports consistent logging. Growth samples go to CSV, reports combine current readings with history, cron schedules work, and backup tools verify archives.'),
('3.2 Linux Environment Setup','On Ubuntu install dependencies with sudo apt update and sudo apt install -y bash coreutils findutils gawk sed grep tar gzip cron. Run chmod +x install.sh bin/*.sh bin/lib/*.sh tests/*.sh and then ./install.sh. The build host was Windows; WSL was denied, so deployment execution remains to be verified on Ubuntu.'),
('3.3 User and Group Management','The project runs under the installing user and creates no daemon account. The user owns the crontab and output files. This avoids extra privileges; local policy may choose a dedicated account.'),
('3.4 File and Directory Management','bin holds executables and common.sh; config stores plain key/value settings; data stores CSV history; logs stores monitor and alert logs; reports holds timestamped reports; backup holds archives/recovery; tests holds integration tests; screenshots documents capture steps; tools builds this report.'),
('3.5 Package and Process Management','Ubuntu apt installs standard utilities and cron. Scripts are short-lived commands, not a daemon. Check cron with systemctl status cron; during active runs, inspect processes with ps and project logs.'),
('3.6 Storage and File System Configuration','No partitions, filesystems, or LVM are modified. df -P -B1 reports byte capacity; df -P -i reports inode counts. Pseudo filesystem types are configurable exclusions. Usage at warning or critical thresholds is written to administrator_alerts.log.'),
('3.7 Backup and Automation','monitor_cycle.sh runs each five minutes; generate_report.sh runs every fifteen minutes. install_cron.sh preserves unrelated crontab entries and replaces only marked project entries. backup_project.sh creates tar.gz and checks it with tar -tzf. restore_backup.sh restricts the source archive and resolved destination to the configured backup directory and rejects symbolic-link escapes.'),
('3.8 Security and Access Control','Installer modes are 750 for scripts/directories and 640 for configuration, logs, and CSV. Configuration is parsed as data, never sourced. Thresholds and paths are validated. Recovery cannot target absolute or parent-traversal paths. Root is unnecessary for monitoring; permission-limited directory sizes are best-effort.')]),
('4. Results and Testing',[
('4.1 Implementation Results','The Bash modules, configuration, cron setup, report generation, CSV initialization, backup/recovery, integration tests, user guides, and editable academic deliverables are present. The integration suite completed under Git for Windows Bash with 9 checks passed and 0 failed; three Linux-only live collection checks were skipped. Bash syntax, threshold alert branches, archive integrity, and selected-file recovery were exercised. Ubuntu filesystem observations and cron scheduling remain to be verified on the target host.'),
('4.2 Testing and Validation','Git Bash was initially blocked by the sandbox, then a reviewed syntax-only and integration run was allowed. The first live run exposed a Windows df source label containing spaces, which does not match the project parser assumptions for Linux df output. The test suite now clearly skips live df, CSV sampling, and report integration on MSYS rather than treating Windows volume data as Linux evidence. WSL still returned Wsl/E_ACCESSDENIED. The table reports actual results and marks all Ubuntu-only behavior NOT EXECUTED.')]),
('5. Conclusion and Future Scope',[
('Conclusion','The project supplies a modular Bash foundation for capacity and inode monitoring, growth history, threshold alerts, reports, cron scheduling, and verified backup recovery. It follows Project 7 and avoids destructive storage simulations.'),
('Future Scope','Possible extensions include retention/rotation, email or webhook notices, trend charts, mount allowlists, robust CSV escaping for unusual mount names, systemd timers, and encrypted off-host backups.')]),
('6. References',[
('References','1. Linux System Administration Hackathon Based DSA-SEE Guidelines, 09.09.26, pp. 14–15. 2. Linux new.pdf, 75 pages, used for report organization and technical context only. 3. GNU Bash Reference Manual. 4. GNU Coreutils manual pages: df, du, date, stat, sort, tail. 5. Ubuntu Server documentation for package management and cron. 6. Debian manual pages: cron(8), crontab(5), tar(1), gzip(1).')]),
('7. Appendices',[
('Appendix A. Editable Cover Details','Student name: [ENTER STUDENT NAME]\nRegister number: [ENTER REGISTER NUMBER]\nFaculty supervisor: [ENTER FACULTY SUPERVISOR]\nAcademic programme: [ENTER ACADEMIC DETAILS]\nSubmission date: [ENTER SUBMISSION DATE]'),
('Appendix B. Project Tree',''),
('Appendix C. Key Commands','./install.sh\n./bin/run_all.sh\n./bin/disk_monitor.sh\n./bin/inode_monitor.sh\n./bin/storage_growth.sh\n./bin/generate_report.sh\n./bin/install_cron.sh\n./bin/backup_project.sh'),
('Appendix D. Screenshot Evidence','Screenshot slots are placeholders for genuine captures on the Ubuntu host. The Windows environment did not provide usable Ubuntu or terminal screenshot capture. See screenshots/README.md for exact commands.')])]

test_rows=[
['Objective','Command / method','Expected output','Actual output','Status'],
['Select project and inspect references','Extract guideline pp. 14–15 and report','Project 7 plus reference structure','Project 7 listed on p. 15; reference report has 75 pages','PASS'],
['Bash syntax','bash -n on install, module, library, and test scripts','No parser errors','Git Bash syntax checks passed','PASS'],
['Disk, inode, history and report integration','./bin/run_all.sh; inspect CSV/report','Mounted filesystem tables and output files','Live Linux checks skipped on MSYS; Windows df labels include spaces','NOT EXECUTED on Ubuntu'],
['Warning and critical alert branches','Test helper at 75% and 90% with TEST-MOUNT label','Alert log contains warning and critical','Both branches and expected log text passed in Git Bash','PASS (helper test)'],
['Backup integrity and selected-file recovery','backup_project.sh; tar -tzf; restore_backup.sh','Valid archive and recovered README','Archive listing and recovery check passed in Git Bash','PASS'],
['Report generation','generate_report.sh','Timestamped report includes usage/history','Requires Ubuntu host','NOT EXECUTED'],
['Cron configuration and timing','install_cron.sh; crontab -l; wait','5-minute monitor, 15-minute report','Cron runtime unavailable here','NOT EXECUTED'],
['Permissions and invalid input','stat; malformed config/path tests','Modes 750/640; invalid values refused','Installer permission changes need Ubuntu; unsafe restore destination rejection passed in Git Bash','PARTIAL']]

def doc_table(doc,rows):
    t=doc.add_table(rows=0,cols=len(rows[0])); t.style='Table Grid'; t.alignment=WD_TABLE_ALIGNMENT.CENTER
    for ri,row in enumerate(rows):
        cells=t.add_row().cells
        for ci,val in enumerate(row):
            cells[ci].text=str(val)
            for p in cells[ci].paragraphs:
                p.paragraph_format.space_after=Pt(1)
                for r in p.runs: r.font.name='Arial'; r.font.size=Pt(7.2); r.bold=(ri==0)
            if ri==0:
                shd=OxmlElement('w:shd'); shd.set(qn('w:fill'),'1F4E78'); cells[ci]._tc.get_or_add_tcPr().append(shd)
                for r in cells[ci].paragraphs[0].runs: r.font.color.rgb=RGBColor(255,255,255)
    return t

doc=Document(); sec=doc.sections[0]; sec.top_margin=Inches(.7); sec.bottom_margin=Inches(.7); sec.left_margin=Inches(.75); sec.right_margin=Inches(.75)
doc.styles['Normal'].font.name='Arial'; doc.styles['Normal'].font.size=Pt(10)
for s in ['Title','Heading 1','Heading 2']:
    doc.styles[s].font.name='Arial'; doc.styles[s].font.color.rgb=RGBColor(31,78,121)
doc.styles['Heading 1'].font.size=Pt(16); doc.styles['Heading 2'].font.size=Pt(12)
header=sec.header.paragraphs[0]; header.text='LINUX SYSTEM ADMINISTRATION  |  E1ITA307'; header.alignment=WD_ALIGN_PARAGRAPH.RIGHT
header.runs[0].font.size=Pt(8); header.runs[0].font.color.rgb=RGBColor(100,110,125)
footer=sec.footer.paragraphs[0]; footer.alignment=WD_ALIGN_PARAGRAPH.CENTER; footer.add_run('Linux Storage Monitoring System  •  ').font.size=Pt(8)
fld=OxmlElement('w:fldSimple'); fld.set(qn('w:instr'),'PAGE'); footer._p.append(fld)
p=doc.add_paragraph(); p.alignment=WD_ALIGN_PARAGRAPH.CENTER
r=p.add_run('\nLINUX SYSTEM ADMINISTRATION (E1ITA307)\n\nLINUX INFRASTRUCTURE DEPLOYMENT PROJECT REPORT\n'); r.bold=True; r.font.size=Pt(17); r.font.color.rgb=RGBColor(31,78,121)
p.add_run('\nON\n\nLINUX STORAGE MONITORING SYSTEM\n\n\nSubmitted by\n[ENTER STUDENT NAME]\n[ENTER REGISTER NUMBER]\n\nUnder the supervision of\n[ENTER FACULTY SUPERVISOR]\n\n[ENTER PROGRAMME / DEPARTMENT]\n[ENTER INSTITUTION]\n[ENTER SUBMISSION DATE]')
doc.add_page_break(); doc.add_heading('Document Note',0); doc.add_paragraph('Editable report for the selected Project 7 implementation. Identity and institutional details remain placeholders. No student identities, signatures, certificates, or approvals from the reference report have been reproduced.')
doc.add_heading('Table of Contents',0)
for title,_ in chapters: doc.add_paragraph(title,style='List Bullet')
doc.add_page_break()
for title,sections in chapters:
    doc.add_heading(title,0)
    for heading,body in sections:
        doc.add_heading(heading,2)
        if heading.startswith('3.1'):
            doc.add_picture(str(ARCH),width=Inches(6.2)); doc.paragraphs[-1].alignment=WD_ALIGN_PARAGRAPH.CENTER
        if heading.startswith('Appendix B'):
            r=doc.add_paragraph().add_run(TREE); r.font.name='Consolas'; r.font.size=Pt(8)
        if body: doc.add_paragraph(body)
        if heading.startswith('3.6'):
            r=doc.add_paragraph().add_run('df -P -B1\ndf -P -i\nawk -F, -v m="$mount" ...'); r.font.name='Consolas'; r.font.size=Pt(9)
        if heading.startswith('3.7'):
            r=doc.add_paragraph().add_run('*/5  * * * *  /path/to/linux-storage-monitor/bin/monitor_cycle.sh\n*/15 * * * *  /path/to/linux-storage-monitor/bin/generate_report.sh'); r.font.name='Consolas'; r.font.size=Pt(9)
        if heading.startswith('4.2'): doc_table(doc,test_rows)
        if heading.startswith('Appendix D'):
            for label in ['Linux environment','Project directory','Disk monitoring','Inode monitoring','Alert generation','Storage history','Generated report','Cron configuration','Backup creation','Backup verification and recovery']:
                t=doc.add_table(rows=1,cols=1); t.style='Table Grid'; t.cell(0,0).text='SCREENSHOT PLACEHOLDER — '+label.upper()+'\nInsert genuine Ubuntu terminal evidence using screenshots/README.md.'
                doc.add_paragraph()
doc.save(DOCX_OUT)

ss=getSampleStyleSheet()
ss.add(ParagraphStyle(name='CoverX',parent=ss['Title'],fontSize=18,leading=24,textColor=colors.HexColor('#1f4e79'),alignment=TA_CENTER,spaceAfter=10))
ss.add(ParagraphStyle(name='H1X',parent=ss['Heading1'],fontSize=15,leading=19,textColor=colors.HexColor('#1f4e79'),spaceBefore=8,spaceAfter=6))
ss.add(ParagraphStyle(name='H2X',parent=ss['Heading2'],fontSize=11,leading=14,textColor=colors.HexColor('#234e70'),spaceBefore=6,spaceAfter=3))
ss.add(ParagraphStyle(name='BodyX',parent=ss['BodyText'],fontSize=8.7,leading=12,spaceAfter=5))
ss.add(ParagraphStyle(name='SmallX',parent=ss['BodyText'],fontSize=6.5,leading=8))
ss.add(ParagraphStyle(name='CodeX',fontName='Courier',fontSize=7,leading=9,leftIndent=8,backColor=colors.HexColor('#f2f4f7'),borderPadding=4))
story=[Spacer(1,25*mm),Paragraph('LINUX SYSTEM ADMINISTRATION (E1ITA307)',ss['BodyX']),Spacer(1,10*mm),Paragraph('LINUX INFRASTRUCTURE DEPLOYMENT<br/>PROJECT REPORT',ss['CoverX']),Paragraph('ON<br/><br/>LINUX STORAGE MONITORING SYSTEM',ss['CoverX']),Spacer(1,10*mm),Paragraph('Submitted by<br/>[ENTER STUDENT NAME]<br/>[ENTER REGISTER NUMBER]<br/><br/>Supervisor: [ENTER FACULTY SUPERVISOR]<br/><br/>[ENTER PROGRAMME / DEPARTMENT]<br/>[ENTER INSTITUTION]<br/>[ENTER SUBMISSION DATE]',ss['BodyX']),PageBreak(),Paragraph('Document Note and Contents',ss['H1X']),Paragraph('Editable report. Identity details remain placeholders; no copied identities, signatures, or approvals are included.',ss['BodyX'])]
story += [Paragraph(t,ss['BodyX']) for t,_ in chapters]+[PageBreak()]
for title,sections in chapters:
    story.append(Paragraph(title,ss['H1X']))
    for heading,body in sections:
        story.append(Paragraph(heading,ss['H2X']))
        if heading.startswith('3.1'): story.append(Image(str(ARCH),width=174*mm,height=99*mm))
        if heading.startswith('Appendix B'): story.append(Preformatted(TREE,ss['CodeX']))
        if body: story.append(Paragraph(body.replace('&','&amp;').replace('\n','<br/>'),ss['BodyX']))
        if heading.startswith('3.6'): story.append(Preformatted('df -P -B1\ndf -P -i\nawk -F, -v m="$mount" ...',ss['CodeX']))
        if heading.startswith('3.7'): story.append(Preformatted('*/5  * * * *  /path/to/linux-storage-monitor/bin/monitor_cycle.sh\n*/15 * * * *  /path/to/linux-storage-monitor/bin/generate_report.sh',ss['CodeX']))
        if heading.startswith('4.2'):
            data=[[Paragraph(str(c),ss['SmallX']) for c in row] for row in test_rows]
            t=Table(data,repeatRows=1,colWidths=[27*mm,34*mm,37*mm,68*mm,18*mm])
            t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#1f4e78')),('TEXTCOLOR',(0,0),(-1,0),colors.white),('GRID',(0,0),(-1,-1),.4,colors.grey),('VALIGN',(0,0),(-1,-1),'TOP'),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#f1f4f8')]),('LEFTPADDING',(0,0),(-1,-1),3),('RIGHTPADDING',(0,0),(-1,-1),3)])); story.append(t)
        if heading.startswith('Appendix D'):
            for label in ['Linux environment','Project directory','Disk monitoring','Inode monitoring','Alert generation','Storage history','Generated report','Cron configuration','Backup creation','Backup verification and recovery']:
                story.extend([Paragraph('SCREENSHOT PLACEHOLDER — '+label.upper()+'. Capture on Ubuntu using screenshots/README.md.',ss['SmallX']),Spacer(1,3*mm)])
def page(canvas,doc):
    canvas.saveState(); canvas.setFont('Helvetica',8); canvas.setFillColor(colors.grey); canvas.drawString(16*mm,9*mm,'Linux Storage Monitoring System  |  E1ITA307'); canvas.drawRightString(194*mm,9*mm,str(doc.page)); canvas.restoreState()
SimpleDocTemplate(str(PDF_OUT),pagesize=A4,rightMargin=15*mm,leftMargin=15*mm,topMargin=15*mm,bottomMargin=16*mm,title='Linux Storage Monitoring System Report',author='[ENTER STUDENT NAME]').build(story,onFirstPage=page,onLaterPages=page)
print(DOCX_OUT); print(PDF_OUT); print(ARCH)
