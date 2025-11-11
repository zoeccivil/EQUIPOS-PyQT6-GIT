"""
Test for Firebase Migrator

Tests the migrator functionality including batch processing, duplicate detection,
and metadata tracking.
"""
import sys
import os
import tempfile
import shutil
import json

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.migration.firebase_migrator import FirebaseMigrator
from logic import DatabaseManager


def test_migrator_initialization():
    """Test migrator can be initialized"""
    print("Test 1: Migrator initialization...")
    
    temp_dir = tempfile.mkdtemp()
    try:
        # Create test database
        temp_db = os.path.join(temp_dir, "test.db")
        db = DatabaseManager(temp_db)
        db.crear_tablas_nucleo()
        
        # Create fake service account
        service_account = {
            'project_id': 'test-project',
            'private_key': 'fake-key'
        }
        sa_path = os.path.join(temp_dir, 'serviceAccount.json')
        with open(sa_path, 'w') as f:
            json.dump(service_account, f)
        
        # Initialize migrator
        migrator = FirebaseMigrator(temp_db, sa_path, dry_run=True)
        
        assert migrator.db_path == temp_db, "DB path should match"
        assert migrator.dry_run == True, "Dry run should be enabled"
        
        # Initialize connections
        assert migrator.initialize_sqlite(), "SQLite should initialize"
        assert migrator.initialize_firebase(), "Firebase should initialize (dry run)"
        
        migrator.close()
        
        print("  ✓ Migrator initialized successfully")
        return True
        
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_table_migration_dry_run():
    """Test table migration in dry-run mode"""
    print("\nTest 2: Table migration (dry run)...")
    
    temp_dir = tempfile.mkdtemp()
    try:
        # Create test database with data
        temp_db = os.path.join(temp_dir, "test.db")
        db = DatabaseManager(temp_db)
        db.crear_tablas_nucleo()
        db.sembrar_datos_iniciales()
        
        # Add some test data
        db.execute("INSERT INTO proyectos (nombre, moneda) VALUES (?, ?)", ("Test Project", "USD"))
        db.execute("INSERT INTO categorias (nombre) VALUES (?)", ("Test Category",))
        
        # Create service account
        service_account = {'project_id': 'test-project', 'private_key': 'fake'}
        sa_path = os.path.join(temp_dir, 'serviceAccount.json')
        with open(sa_path, 'w') as f:
            json.dump(service_account, f)
        
        # Initialize migrator
        migrator = FirebaseMigrator(temp_db, sa_path, dry_run=True)
        migrator.initialize_sqlite()
        migrator.initialize_firebase()
        
        # Migrate proyectos table
        migrated, skipped, errors = migrator.migrate_table('proyectos')
        
        assert migrated > 0, "Should have migrated at least 1 proyecto"
        assert errors == 0, "Should have no errors"
        
        print(f"  ✓ Migrated {migrated} proyectos (dry run)")
        
        # Check stats
        assert migrator.stats['total_records'] > 0, "Should have counted records"
        assert migrator.stats['migrated'] == migrated, "Stats should match"
        
        print(f"  ✓ Statistics tracking working")
        
        migrator.close()
        return True
        
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_document_preparation():
    """Test document preparation with metadata"""
    print("\nTest 3: Document preparation...")
    
    temp_dir = tempfile.mkdtemp()
    try:
        temp_db = os.path.join(temp_dir, "test.db")
        sa_path = os.path.join(temp_dir, 'serviceAccount.json')
        
        with open(sa_path, 'w') as f:
            json.dump({'project_id': 'test', 'private_key': 'fake'}, f)
        
        migrator = FirebaseMigrator(temp_db, sa_path, dry_run=True)
        
        # Test record
        record = {
            'id': 123,
            'nombre': 'Test',
            'fecha': '2025-01-01'
        }
        
        # Prepare document
        doc = migrator._prepare_document(record, 'test_table')
        
        assert 'original_sqlite_id' in doc, "Should have original_sqlite_id"
        assert doc['original_sqlite_id'] == 123, "Should preserve ID"
        assert 'migrated_at' in doc, "Should have migrated_at"
        assert 'migrated_by' in doc, "Should have migrated_by"
        assert 'source_table' in doc, "Should have source_table"
        assert doc['source_table'] == 'test_table', "Should preserve table name"
        
        print("  ✓ Document metadata added correctly")
        print(f"  ✓ Metadata fields: {list(doc.keys())}")
        
        return True
        
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_migration_artifacts():
    """Test that migration artifacts are created"""
    print("\nTest 4: Migration artifacts...")
    
    temp_dir = tempfile.mkdtemp()
    try:
        # Setup
        temp_db = os.path.join(temp_dir, "test.db")
        db = DatabaseManager(temp_db)
        db.crear_tablas_nucleo()
        
        sa_path = os.path.join(temp_dir, 'serviceAccount.json')
        with open(sa_path, 'w') as f:
            json.dump({'project_id': 'test', 'private_key': 'fake'}, f)
        
        migrator = FirebaseMigrator(temp_db, sa_path, dry_run=True)
        migrator.initialize_sqlite()
        migrator.initialize_firebase()
        
        # Run migration
        migrator.migrate_table('proyectos')
        
        # Save artifacts
        os.chdir(temp_dir)  # Change to temp dir for file creation
        
        migrator.save_mapping('mapping.json')
        assert os.path.exists('mapping.json'), "Mapping file should be created"
        print("  ✓ mapping.json created")
        
        migrator.save_log('migration_log.txt')
        assert os.path.exists('migration_log.txt'), "Log file should be created"
        
        # Check log content
        with open('migration_log.txt', 'r') as f:
            log_content = f.read()
        assert 'proyectos' in log_content, "Log should mention migrated table"
        print("  ✓ migration_log.txt created with content")
        
        migrator.save_summary('migration_summary.json')
        assert os.path.exists('migration_summary.json'), "Summary file should be created"
        
        # Check summary content
        with open('migration_summary.json', 'r') as f:
            summary = json.load(f)
        
        assert 'timestamp' in summary, "Summary should have timestamp"
        assert 'dry_run' in summary, "Summary should indicate dry run"
        assert summary['dry_run'] == True, "Should be marked as dry run"
        assert 'statistics' in summary, "Summary should have statistics"
        
        print("  ✓ migration_summary.json created with statistics")
        print(f"  ✓ Statistics: {summary['statistics']}")
        
        migrator.close()
        return True
        
    finally:
        os.chdir('/')  # Change back
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_batch_processing():
    """Test batch processing with large number of records"""
    print("\nTest 5: Batch processing...")
    
    temp_dir = tempfile.mkdtemp()
    try:
        # Create database with many records
        temp_db = os.path.join(temp_dir, "test.db")
        db = DatabaseManager(temp_db)
        db.crear_tablas_nucleo()
        
        # Add 1200 categories (more than 2 batches of 500)
        for i in range(1200):
            db.execute("INSERT INTO categorias (nombre) VALUES (?)", (f"Category {i}",))
        
        sa_path = os.path.join(temp_dir, 'serviceAccount.json')
        with open(sa_path, 'w') as f:
            json.dump({'project_id': 'test', 'private_key': 'fake'}, f)
        
        migrator = FirebaseMigrator(temp_db, sa_path, dry_run=True)
        migrator.initialize_sqlite()
        migrator.initialize_firebase()
        
        # Migrate with batch size 500
        migrated, skipped, errors = migrator.migrate_table('categorias', batch_size=500)
        
        assert migrated == 1200, f"Should have migrated all 1200 records, got {migrated}"
        assert errors == 0, "Should have no errors"
        
        # Check that batching was logged
        assert len(migrator.migration_log) > 0, "Should have log entries"
        
        # Count batch messages (should be at least 3 batches: 500, 500, 200)
        batch_logs = [log for log in migrator.migration_log if 'batch' in log.lower()]
        assert len(batch_logs) >= 3, f"Should have at least 3 batch logs, got {len(batch_logs)}"
        
        print(f"  ✓ Processed 1200 records in batches")
        print(f"  ✓ Found {len(batch_logs)} batch log entries")
        
        migrator.close()
        return True
        
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("Testing Firebase Migrator (PR5)")
    print("=" * 60)
    
    tests = [
        test_migrator_initialization,
        test_table_migration_dry_run,
        test_document_preparation,
        test_migration_artifacts,
        test_batch_processing
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"\n✗ Test failed with exception: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
    
    print("\n" + "=" * 60)
    if all(results):
        print("All tests passed! ✓")
        print("=" * 60)
        return True
    else:
        print(f"Some tests failed: {sum(results)}/{len(results)} passed")
        print("=" * 60)
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
