# Firebase Migrator Implementation (PR5)

## Overview

The Firebase Migrator is the actual implementation that performs the migration from SQLite to Firebase Firestore and Cloud Storage. It's used by the Migration UI (PR4) to execute migrations.

## Architecture

```
┌─────────────────────────────────┐
│  DialogoMigracionFirebase (UI)  │
│         (PR4)                    │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│    MigrationWorker (QThread)    │
│    (runs in background)         │
└──────────────┬──────────────────┘
               │
               ▼
┌─────────────────────────────────┐
│    FirebaseMigrator             │
│    (core migration logic)       │
│         (PR5)                    │
└─────────────────────────────────┘
```

## Features

### 1. Batch Processing
- Processes records in batches of ≤500 documents
- Optimizes Firestore write operations
- Respects Firestore batch limits
- Progress tracking per batch

### 2. Duplicate Detection
- Uses `original_sqlite_id` to identify duplicates
- Queries Firestore before inserting
- Skips records that already exist
- Logs skipped records for review

### 3. Metadata Tracking
Each migrated document includes:
- `original_sqlite_id`: Original ID from SQLite
- `migrated_at`: ISO 8601 timestamp
- `migrated_by`: "FirebaseMigrator"
- `source_table`: Name of SQLite table

### 4. Attachment Upload
- Uploads files from `conduce_adjunto_path` to Cloud Storage
- Organized path: `projects/{proyecto_id}/conduces/{transaccion_id}/{filename}`
- Stores `storage_path` and `public_url` in document
- Handles missing files gracefully

### 5. Migration Artifacts
Generated files (excluded from git via `.gitignore`):

**mapping.json**
```json
{
  "proyectos_1": "firestore-doc-id-xyz",
  "equipos_5": "firestore-doc-id-abc",
  ...
}
```

**migration_log.txt**
```
[2025-01-11 10:30:00] Migration started
[2025-01-11 10:30:01] SQLite database opened: progain_database.db
[2025-01-11 10:30:02] Migrating table: proyectos
[2025-01-11 10:30:02]   Found 15 records in proyectos
[2025-01-11 10:30:03]   Processing batch 1/1 (15 records)
[2025-01-11 10:30:04]   ✓ proyectos: 15 migrated, 0 skipped, 0 errors
...
```

**migration_summary.json**
```json
{
  "timestamp": "2025-01-11T10:35:00.000",
  "dry_run": false,
  "database": "progain_database.db",
  "firebase_project": "progain-production",
  "statistics": {
    "total_records": 1234,
    "migrated": 1200,
    "skipped": 34,
    "errors": 0,
    "conflicts": 0
  },
  "total_tables": 9
}
```

## Usage

### Programmatic Usage

```python
from app.migration.firebase_migrator import FirebaseMigrator

# Initialize
migrator = FirebaseMigrator(
    db_path="progain_database.db",
    service_account_path="serviceAccount.json",
    dry_run=False  # Set to True for preview
)

# Setup connections
migrator.initialize_sqlite()
migrator.initialize_firebase()

# Migrate tables
migrator.migrate_table('proyectos')
migrator.migrate_table('equipos')
migrator.migrate_table('transacciones')

# Upload attachments
migrator.migrate_attachments('transacciones', 'conduce_adjunto_path')

# Save artifacts
migrator.save_mapping()
migrator.save_log()
migrator.save_summary()

# Cleanup
migrator.close()
```

### Via UI (Recommended)

Use the Firebase Migration Dialog:
1. Open "Herramientas > Migrar a Firebase"
2. Select database and credentials
3. Choose tables
4. Run dry-run first
5. Execute actual migration

## Implementation Details

### SQLite to Firestore Type Conversion

| SQLite Type | Firestore Type | Notes |
|-------------|----------------|-------|
| INTEGER | number | Direct conversion |
| REAL | number | Direct conversion |
| TEXT | string | Direct conversion |
| BLOB | bytes | Base64 encoded |
| DATE (YYYY-MM-DD) | Timestamp | Converted to Firestore Timestamp |
| NULL | null | Preserved |

### Batch Processing Algorithm

```python
total = len(records)
batch_size = 500

for i in range(0, total, batch_size):
    batch = records[i:i + batch_size]
    
    # Check for duplicates
    for record in batch:
        existing = firestore_db.collection(collection_name)\
            .where('original_sqlite_id', '==', record['id'])\
            .limit(1).get()
        
        if not existing:
            # Add metadata
            doc_data = prepare_document(record)
            
            # Write to Firestore
            doc_ref = firestore_db.collection(collection_name).add(doc_data)
            
            # Track mapping
            mapping[f"{table}_{record['id']}"] = doc_ref[1].id
```

### Dry Run Mode

In dry-run mode:
- All queries are executed (to count records)
- No writes to Firestore
- No uploads to Cloud Storage
- Duplicate detection runs (to find conflicts)
- Full logging and statistics
- Artifacts are still generated (for review)

Benefits:
- Estimate time and cost
- Identify issues before migration
- Verify data integrity
- Plan for conflicts

## Error Handling

### SQLite Errors
- Connection failures: Logged and migration aborts
- Table not found: Table skipped, logged as error
- Read errors: Record skipped, continues with next

### Firestore Errors
- Authentication: Migration aborts with clear error
- Permission denied: Table skipped, logged
- Write failures: Record logged, continues
- Quota exceeded: Batch waits, retries

### Storage Errors
- File not found: Logged as warning, continues
- Upload failure: Logged, continues with next
- Permission issues: Logged, continues

### Recovery
- Migration can be re-run (duplicates are skipped)
- Partial migrations are valid
- Use mapping.json to verify what was migrated
- Check migration_log.txt for errors

## Performance Considerations

### Optimization Tips

1. **Batch Size**: Default 500 is optimal for Firestore
2. **Network**: Run from location close to Firebase region
3. **Database Size**: Large databases (>10K records) take time
4. **Attachments**: Large files increase migration time
5. **Dry Run**: Always run first to estimate

### Estimated Times

| Records | Estimated Time | Notes |
|---------|----------------|-------|
| 100 | 1-2 minutes | Including setup |
| 1,000 | 5-10 minutes | Single table |
| 10,000 | 30-60 minutes | Multiple tables |
| 100,000 | 3-5 hours | Consider batching by table |

### Cost Estimation

**Firestore Writes:**
- Each record = 1 write
- Batch write = sum of individual writes
- Free tier: 20K writes/day
- Paid: $0.18 per 100K writes

**Cloud Storage:**
- Based on file size
- Free tier: 5GB storage, 1GB/day download
- Paid: $0.026/GB/month

**Example:**
- 10,000 records = 10,000 writes = $0.018
- 500MB attachments = $0.013/month
- Total first month: ~$0.03

## Testing

Run the test suite:

```bash
python test_firebase_migrator.py
```

Tests verify:
1. ✓ Migrator initialization
2. ✓ Table migration (dry run)
3. ✓ Document preparation with metadata
4. ✓ Migration artifacts generation
5. ✓ Batch processing (1200 records)

All tests use temporary databases and don't require Firebase.

## Security

### Credentials
- Never commit `serviceAccount.json`
- Store outside repository
- Use environment variables in production
- Rotate keys periodically

### Firestore Rules
Example rules (deploy manually):

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Only authenticated users
    match /{document=**} {
      allow read: if request.auth != null;
      allow write: if request.auth != null && 
                     request.auth.token.admin == true;
    }
  }
}
```

### Storage Rules
Example rules (deploy manually):

```javascript
rules_version = '2';
service firebase.storage {
  match /b/{bucket}/o {
    match /projects/{projectId}/conduces/{allPaths=**} {
      allow read: if request.auth != null;
      allow write: if request.auth != null &&
                     request.auth.token.admin == true;
    }
  }
}
```

## Troubleshooting

### Common Issues

**"Failed to initialize Firebase"**
- Check service account JSON is valid
- Verify project_id and private_key are present
- Ensure Firebase Admin SDK is installed

**"Permission denied"**
- Check service account has required roles
- Verify Firestore API is enabled
- Check Storage API is enabled

**"Quota exceeded"**
- Check Firebase usage dashboard
- Consider upgrading to Blaze plan
- Reduce batch size
- Migrate tables separately

**"Migration too slow"**
- Check network connection
- Reduce batch size (try 100 or 250)
- Migrate during off-peak hours
- Consider regional proximity

## Next Steps

After successful migration:

1. **Verify Data**
   - Open Firebase Console
   - Check Firestore collections
   - Verify record counts match
   - Test queries

2. **Implement Firestore Repository** (Future PR)
   - Create `FirestoreRepository` class
   - Implement `AbstractRepository` interface
   - Add to `RepositoryFactory`
   - Switch app to use Firestore

3. **Configure Security Rules**
   - Deploy Firestore rules
   - Deploy Storage rules
   - Test with different user roles

4. **Monitor & Optimize**
   - Watch Firebase usage
   - Check query performance
   - Add indexes as needed
   - Optimize read patterns

## Support

For issues:
1. Check `migration_log.txt` for details
2. Review `migration_summary.json` for statistics
3. Verify `mapping.json` for ID mappings
4. Consult Firebase Console for server-side errors
5. Check test suite passes: `python test_firebase_migrator.py`

## References

- [Firestore Documentation](https://firebase.google.com/docs/firestore)
- [Cloud Storage Documentation](https://firebase.google.com/docs/storage)
- [Firebase Admin SDK](https://firebase.google.com/docs/admin/setup)
- [Firestore Pricing](https://firebase.google.com/pricing)
