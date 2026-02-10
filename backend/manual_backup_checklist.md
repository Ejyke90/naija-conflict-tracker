# Manual Database Backup Checklist

## 🚨 CRITICAL: Complete this BEFORE migration

### Current Status
- **Migration Type**: Kidnapping data migration (1,260 records)
- **Risk Level**: HIGH (complete data replacement)
- **Backup Required**: YES

### Backup Options

#### Option 1: Railway Dashboard Backup (Recommended)
1. Go to Railway dashboard
2. Select your database service
3. Click "Data" tab
4. Click "Create Backup"
5. Wait for backup completion
6. Download backup file

#### Option 2: External Tool Backup
```bash
# Using DBeaver or similar GUI tool
1. Connect to database with DATABASE_URL
2. Right-click database -> Tools -> Backup
3. Choose SQL format
4. Save as: manual_backup_YYYYMMDD.sql
```

#### Option 3: Command Line (if pg_dump version matches)
```bash
# Check PostgreSQL versions
pg_dump --version
# Should match server version (17.7)

# If versions match:
PGPASSWORD=npg_bL6dDyw8WEMI pg_dump \
  --host=ep-gentle-union-agwmnyzn-pooler.c-2.eu-central-1.aws.neon.tech \
  --port=5432 \
  --username=neondb_owner \
  --dbname=neondb \
  --verbose \
  --clean \
  --no-acl \
  --no-owner \
  -f manual_backup_$(date +%Y%m%d_%H%M%S).sql
```

### Verification Checklist
- [ ] Backup file created successfully
- [ ] Backup file size > 0 (should be several MB)
- [ ] Backup contains conflicts table data
- [ ] Backup file can be opened in text editor
- [ ] Current kidnapping records count: **13** (verify this matches backup)

### Restore Test (Optional but Recommended)
```bash
# Create test database and restore backup to verify integrity
psql $DATABASE_URL_TEST < manual_backup_YYYYMMDD_HHMMSS.sql
```

### Migration Proceed Checklist
- [ ] Backup completed and verified
- [ ] Backup file stored safely
- [ ] Ready to proceed with migration
- [ ] Rollback plan documented

---

## ⚠️  DO NOT PROCEED WITHOUT COMPLETED BACKUP

**Current Migration Impact:**
- Replacing 13 records with 1,260 records
- 9,700% increase in data volume
- High risk of data corruption during migration

**If backup fails:**
- Stop migration immediately
- Contact database administrator
- Do not attempt manual data modification
