# Firebase Migration Guide

## Overview

This guide explains how to use the Firebase Migration UI to migrate your SQLite database to Firebase Firestore and Cloud Storage.

## Important Security Notes

⚠️ **CRITICAL:** Never commit Firebase credentials to the repository!

- The `serviceAccount.json` file is excluded via `.gitignore`
- Keep your credentials file outside the repository directory
- Use the same Firebase project that the PROGAIN ecosystem already uses

## Prerequisites

1. **SQLite Database**: Your current `progain_database.db` file
2. **Firebase Credentials**: `serviceAccount.json` file from Firebase Console
3. **Firebase Project**: Use the existing PROGAIN Firebase project (same projectId)

### Getting Firebase Credentials

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Select the PROGAIN project
3. Go to Project Settings → Service Accounts
4. Click "Generate New Private Key"
5. Download and save as `serviceAccount.json` (keep it secure!)

## Using the Migration Dialog

### Opening the Dialog

1. Launch the application
2. Go to menu: **Herramientas → Migrar a Firebase...**
3. The migration dialog will open

### Dialog Sections

#### 1. Configuration

**Base de datos SQLite:**
- Click "Seleccionar..." to choose your `.db` file
- By default, it loads the current database being used

**Credenciales Firebase:**
- Click "Seleccionar..." to choose your `serviceAccount.json` file
- The dialog will validate the credentials and show the project ID
- ⚠️ Warning is displayed to remind you not to commit this file

#### 2. Tables Selection

- **Default**: All tables are selected
- **Select All**: Check all tables at once
- **Deselect All**: Uncheck all tables

**Available Tables:**
- `proyectos` - Projects
- `cuentas` - Accounts
- `categorias` - Categories
- `equipos` - Equipment
- `transacciones` - Transactions
- `equipos_entidades` - Entities (Clients/Operators)
- `equipos_alquiler_meta` - Rental metadata
- `pagos` - Payments
- `mantenimientos` - Maintenance records

#### 3. Options

**Dry Run** (Recommended for first run):
- Enabled by default
- Only counts records and detects conflicts
- No actual data is written to Firestore
- Useful to verify migration will work

**Create Backup**:
- Enabled by default
- Creates a timestamped backup in `backups/` folder
- Format: `backup_[dbname]_YYYYMMDD_HHMMSS`
- Only runs if Dry Run is disabled

#### 4. Progress

Shows:
- Current operation status
- Progress bar (0-100%)
- Real-time updates during migration

#### 5. Logs

- Timestamped log entries
- Shows each step of the migration
- Errors and warnings are displayed here
- Review logs after migration completes

### Migration Workflow

#### First Time: Dry Run

1. Select your database and credentials
2. Choose tables to migrate
3. **Keep "Dry Run" checked**
4. Click "Iniciar Migración"
5. Review the logs:
   - Count of records per table
   - Any conflicts detected
   - Estimated time and cost

#### Actual Migration

1. If dry run was successful:
2. **Uncheck "Dry Run"**
3. **Keep "Create Backup" checked**
4. Click "Iniciar Migración"
5. Wait for completion (do not close the dialog)
6. Review logs and success message

## Migration Process Details

### What Gets Migrated

For each table:
1. **Records**: All data rows from SQLite
2. **Metadata**: Additional fields added:
   - `original_sqlite_id`: Original ID from SQLite
   - `migrated_at`: Timestamp of migration
   - `migrated_by`: User/system that ran migration
3. **Attachments**: Files are uploaded to Cloud Storage
   - Path: `projects/{proyecto_id}/conduces/{transaccion_id}/{filename}`
   - URLs are stored in Firestore documents

### Duplicate Detection

The migrator checks for existing records using `original_sqlite_id`:
- If a record already exists in Firestore, it's skipped
- The log will show: "Record already migrated"
- This prevents duplicates on re-runs

### Batch Processing

- Records are migrated in batches of ≤500
- This optimizes Firestore write costs
- Progress updates after each batch

## After Migration

### Files Generated

1. **mapping.json**: Maps SQLite IDs to Firestore document IDs
2. **migration_log.txt**: Detailed log of entire migration
3. **migration_summary.json**: Statistics and summary
4. **Backup** (if enabled): Complete database backup

These files are created in the application directory and are excluded from git via `.gitignore`.

### Verification

1. Open Firebase Console
2. Go to Firestore Database
3. Verify collections and documents exist
4. Check Cloud Storage for uploaded files
5. Run test queries to ensure data integrity

## Troubleshooting

### "Credenciales inválidas"

- Verify you downloaded the correct `serviceAccount.json`
- Check that the file contains `project_id` and `private_key`
- Ensure you're using the PROGAIN project credentials

### "Permission denied"

- Check Firebase IAM permissions for the service account
- Service account needs:
  - Firestore Editor
  - Storage Admin
  - Firebase Admin SDK Administrator

### Migration Fails Partway

1. Check the logs for specific error
2. The migration can be re-run (duplicates are skipped)
3. Consider migrating tables individually if one is problematic

### Large Database Performance

For databases with many records:
- Dry run first to estimate time
- Migrate during off-peak hours
- Consider migrating tables separately
- Monitor Firebase quotas and billing

## Cost Considerations

### Firestore Writes

- Each record = 1 write operation
- Batch writes are still counted individually
- [Firestore Pricing](https://firebase.google.com/pricing)

### Cloud Storage

- Based on storage size and operations
- Conduces/attachments add to storage costs
- Consider compression for large files

### Recommendations

1. Start with dry run to estimate costs
2. Archive or delete unused records before migrating
3. Migrate test data first to gauge costs
4. Monitor Firebase billing dashboard

## Best Practices

1. **Always run dry run first**
2. **Create backups before actual migration**
3. **Migrate during low-traffic periods**
4. **Test with small dataset first**
5. **Keep credentials secure and outside repo**
6. **Document any custom mappings or transformations**
7. **Verify data after migration**
8. **Keep SQLite backup until Firestore is proven stable**

## Support

For issues or questions:
1. Check the logs in the migration dialog
2. Review `migration_log.txt` for details
3. Consult Firebase documentation
4. Check Firestore console for data

## Security Checklist

- [ ] `serviceAccount.json` is NOT in the repository
- [ ] `.gitignore` includes Firebase credential patterns
- [ ] Firestore security rules are configured
- [ ] Cloud Storage security rules are configured
- [ ] Service account has minimum necessary permissions
- [ ] Backup files are secured/encrypted
- [ ] Migration logs don't contain sensitive data

## Next Steps

After successful migration:
1. Update application to use Firebase repository (PR5)
2. Configure Firestore and Storage security rules
3. Test all CRUD operations with Firestore
4. Plan for ongoing sync if needed
5. Decommission SQLite or keep as backup
