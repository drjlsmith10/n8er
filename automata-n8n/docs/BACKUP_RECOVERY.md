# Project Automata: Backup and Recovery Guide

**Version:** 2.0.0-alpha
**Last Updated:** 2025-11-20
**Status:** Active

---

## Overview

This guide covers backup and disaster recovery procedures for Project Automata. The system generates valuable knowledge base data and workflows that should be protected against data loss.

### What Gets Backed Up?

- **Knowledge Base** - Community-learned patterns, error solutions, best practices
- **Workflows** - Generated and sample workflow definitions
- **Logs** - System logs for audit and troubleshooting
- **Configuration** - config.py and requirements.txt

### What's NOT Backed Up?

- `.env` files (never backup secrets)
- Virtual environment directories
- Cache files (`__pycache__`, `.pytest_cache`)
- Git history (backup separately if needed)

---

## Automated Backup Strategy

### Recommended Schedule

- **Daily:** Incremental backups during off-peak hours
- **Weekly:** Full backup with verification
- **Monthly:** Validated backup stored in separate location
- **Retention:** Keep 30 days of daily backups

### Backup Sizing

| Component | Typical Size | Growth Rate |
|-----------|--------------|-------------|
| Knowledge Base | 1-5 MB | Slow (patterns accumulate) |
| Workflows | 2-10 MB | Medium (generated workflows) |
| Logs | 5-50 MB | Fast (per GB, depends on log level) |
| **Total** | **10-65 MB** | **Daily: +100KB typical** |

---

## Manual Backup Procedures

### Creating a Backup

```bash
# Basic backup (with defaults)
./scripts/backup_knowledge_base.sh

# Backup to specific directory
./scripts/backup_knowledge_base.sh /backup/automata

# Backup with custom retention (60 days)
./scripts/backup_knowledge_base.sh /backup/automata 60
```

### Backup Output

```
[INFO] 2025-11-20 12:00:01 - Starting Project Automata backup process
[INFO] 2025-11-20 12:00:01 - Backup Directory: /home/automata/backups
[INFO] 2025-11-20 12:00:01 - Retention Period: 30 days
[INFO] 2025-11-20 12:00:01 - Checking prerequisites...
[INFO] 2025-11-20 12:00:02 - Creating backup archive...
[INFO] 2025-11-20 12:00:05 - Backup archive created successfully
[INFO] 2025-11-20 12:00:05 - Verifying backup integrity...
[INFO] 2025-11-20 12:00:05 - Backup integrity verified

========================================
Backup Summary
========================================
Status: SUCCESS
Backup Name: automata_backup_20251120_120000
Location: /home/automata/backups/automata_backup_20251120_120000.tar.gz
Size: 2.5M
Timestamp: 20251120_120000
Manifest: /home/automata/backups/automata_backup_20251120_120000.manifest
========================================
```

### Backup Files

Each backup creates two files:

1. **Archive:** `automata_backup_YYYYMMDD_HHMMSS.tar.gz`
   - Compressed archive containing all backed-up data
   - Typical size: 2-10 MB

2. **Manifest:** `automata_backup_YYYYMMDD_HHMMSS.manifest`
   - Metadata about the backup
   - Contents list
   - Restoration instructions

---

## Restoration Procedures

### Restoring from Backup

```bash
# Restore to current directory
./scripts/restore_knowledge_base.sh backups/automata_backup_20251120_120000.tar.gz

# Restore to specific directory
./scripts/restore_knowledge_base.sh \
  backups/automata_backup_20251120_120000.tar.gz \
  /opt/automata

# Restore to test environment
./scripts/restore_knowledge_base.sh \
  /backup/archive/automata_backup_20251115_100000.tar.gz \
  /tmp/automata_test
```

### Restoration Output

```
[INFO] 2025-11-20 12:05:01 - Starting Project Automata restoration process
[INFO] 2025-11-20 12:05:01 - Backup File: backups/automata_backup_20251120_120000.tar.gz
[INFO] 2025-11-20 12:05:01 - Target Directory: .
[STEP] 2025-11-20 12:05:01 - Verifying backup integrity...
[INFO] 2025-11-20 12:05:02 - Backup integrity verified
[STEP] 2025-11-20 12:05:02 - Listing backup contents...
[STEP] 2025-11-20 12:05:02 - Extracting backup archive...
[INFO] 2025-11-20 12:05:05 - Backup extracted successfully

========================================
Restoration Summary
========================================
Status: SUCCESS
Backup File: backups/automata_backup_20251120_120000.tar.gz
Target Directory: .
Restored At: Tue Nov 20 12:05:05 UTC 2025
========================================
```

### Automatic Pre-Restoration Backup

The restore script automatically creates a backup of existing data:

```
$TARGET_DIR/.pre_restore_backup_YYYYMMDD_HHMMSS/
├── knowledge_base/
└── workflows/
```

This allows rollback if restoration fails or produces unexpected results.

---

## Disaster Recovery Scenarios

### Scenario 1: Knowledge Base Corruption

**Problem:** Knowledge base files are corrupted or data is lost.

**Steps:**
```bash
# 1. Stop the application
systemctl stop automata

# 2. Restore from latest backup
./scripts/restore_knowledge_base.sh backups/latest_backup.tar.gz

# 3. Verify restoration
ls -la knowledge_base/

# 4. Run tests to verify functionality
pytest tests/ -v

# 5. Restart application
systemctl start automata
```

### Scenario 2: Accidental Data Deletion

**Problem:** Critical workflows or patterns were deleted.

**Steps:**
```bash
# 1. Find backup from before deletion
ls -lt backups/*.tar.gz | head -10

# 2. Extract specific file from backup
tar -xzf backups/automata_backup_20251120_090000.tar.gz \
  workflows/my_workflow.json -O > /tmp/my_workflow.json

# 3. Verify the file
cat /tmp/my_workflow.json

# 4. Copy to correct location if verified
cp /tmp/my_workflow.json workflows/my_workflow.json
```

### Scenario 3: Full System Failure

**Problem:** Entire system needs to be rebuilt from scratch.

**Steps:**
```bash
# 1. Set up new system
mkdir -p /opt/automata
cd /opt/automata

# 2. Clone repository
git clone https://github.com/drjlsmith10/n8er.git
cd n8er/automata-n8n

# 3. Restore backup
./scripts/restore_knowledge_base.sh \
  /path/to/backup/automata_backup_20251120_120000.tar.gz \
  ./

# 4. Install dependencies
pip install -r requirements.txt

# 5. Verify restoration
pytest tests/ -v

# 6. Start application
python skills/generate_workflow_json.py --help
```

---

## Backup Best Practices

### 1. Multiple Storage Locations

```bash
# Store backups in multiple locations
./scripts/backup_knowledge_base.sh ./backups              # Local
rsync -av ./backups/ /mnt/nas/automata_backup/           # NAS
s3cmd sync ./backups/ s3://my-bucket/automata/backups/   # Cloud (S3)
```

### 2. Regular Testing

```bash
# Test restoration quarterly
TEST_DIR=$(mktemp -d)
./scripts/restore_knowledge_base.sh ./backups/latest.tar.gz $TEST_DIR
pytest $TEST_DIR/tests/ -v
rm -rf $TEST_DIR
```

### 3. Automated Backup Scheduling

```bash
# Add to crontab for daily backups at 2 AM
0 2 * * * cd /home/automata && ./scripts/backup_knowledge_base.sh

# Add to crontab for weekly validation
0 3 * * 0 cd /home/automata && ./scripts/test_backup_restoration.sh
```

### 4. Monitor Backup Status

```bash
# Check recent backups
ls -lh backups/*.tar.gz | tail -5

# Verify backup sizes are reasonable
du -h backups/

# Check for backup errors
grep ERROR backups/*.manifest
```

### 5. Document Recovery Procedures

- Keep restoration procedures documented and accessible
- Maintain an inventory of backup locations
- Document recovery time objectives (RTO)
- Document recovery point objectives (RPO)

---

## Backup Verification Checklist

Use this checklist before considering a backup valid:

- [ ] Backup file exists and is readable
- [ ] Backup size is reasonable (> 1 MB)
- [ ] Manifest file exists and is recent
- [ ] Tar integrity verification passes
- [ ] Test restoration to temporary directory
- [ ] Verify restored data integrity
- [ ] Confirm all expected files are present
- [ ] Clean up test directory
- [ ] Document backup completion

---

## Troubleshooting

### Issue: "tar not found"

```bash
# Install tar
# Ubuntu/Debian
sudo apt-get install tar gzip

# RHEL/CentOS
sudo yum install tar gzip

# macOS
brew install gnu-tar
```

### Issue: "Backup integrity verification failed"

```bash
# The backup file is corrupted
# Attempt recovery from previous backup
ls -lt backups/automata_backup_*.tar.gz
./scripts/restore_knowledge_base.sh backups/PREVIOUS_BACKUP.tar.gz
```

### Issue: "Permission denied" during backup

```bash
# Ensure script is executable
chmod +x ./scripts/backup_knowledge_base.sh
chmod +x ./scripts/restore_knowledge_base.sh

# Ensure write permissions in backup directory
mkdir -p backups
chmod 755 backups
```

### Issue: "Disk space full"

```bash
# Clean up old backups
./scripts/backup_knowledge_base.sh backups 14  # Keep only 14 days

# Or manually remove old backups
rm -f backups/automata_backup_2025110*.tar.gz

# Check disk space
df -h
du -sh knowledge_base workflows logs
```

---

## Recovery Time Objectives (RTO)

| Scenario | RTO | Notes |
|----------|-----|-------|
| Minor data loss | 15 minutes | Restore specific file |
| Corruption detected | 30 minutes | Full restoration with testing |
| System failure | 1-2 hours | Full rebuild + restore |
| Complete loss | 2-4 hours | Infrastructure setup + restore |

---

## Backup Retention Policy

| Backup Type | Retention | Storage Location |
|-------------|-----------|------------------|
| Daily | 30 days | Local (backups/) |
| Weekly | 12 weeks | Local + NAS |
| Monthly | 12 months | Offsite (Cloud) |
| Annual | Indefinite | Cold storage |

---

## Monitoring and Alerts

### Backup Success Indicators

✓ Backup file created
✓ Archive integrity verified
✓ Manifest file generated
✓ Size is reasonable (> 1 MB)
✓ Recent timestamp (last 24 hours)

### Backup Failure Alerts

⚠️ No backup in last 48 hours
⚠️ Backup file size unusually small (< 1 MB)
⚠️ Archive integrity check failed
⚠️ Manifest file missing
⚠️ Disk space < 10% remaining

---

## References

- Backup Scripts: `scripts/backup_knowledge_base.sh`, `scripts/restore_knowledge_base.sh`
- Configuration: `config.py`
- Manifest Examples: `backups/*.manifest`

For questions or issues with backup/recovery, see [CONTRIBUTING.md](CONTRIBUTING.md)

---

**Last Updated:** 2025-11-20
**Status:** Active
**Maintained By:** Project Automata Team
