"""
Test for Firebase Migration Dialog

Tests the migration dialog UI and basic functionality without requiring PyQt6.
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_dialog_structure():
    """Test that the dialog class is properly structured"""
    print("Test: Dialog structure and imports...")
    
    try:
        # Try importing without PyQt6 (will fail, but we can check the module structure)
        import importlib.util
        
        dialog_path = os.path.join(
            os.path.dirname(__file__),
            'app/ui/dialogs/dialogo_migracion_firebase.py'
        )
        
        # Check file exists
        assert os.path.exists(dialog_path), f"Dialog file not found: {dialog_path}"
        print(f"  ✓ Dialog file exists: {dialog_path}")
        
        # Check file content
        with open(dialog_path, 'r') as f:
            content = f.read()
            
        # Verify key components
        assert 'class DialogoMigracionFirebase' in content, "DialogoMigracionFirebase class not found"
        assert 'class MigrationWorker' in content, "MigrationWorker class not found"
        assert 'def _init_ui' in content, "_init_ui method not found"
        assert 'def _start_migration' in content, "_start_migration method not found"
        assert 'def _abort_migration' in content, "_abort_migration method not found"
        assert 'def _create_backup' in content, "_create_backup method not found"
        assert 'serviceAccount.json' in content, "Service account reference not found"
        
        print("  ✓ All key components found in dialog")
        
        # Check for security warnings
        assert 'gitignore' in content.lower(), "No reference to .gitignore found"
        assert 'no subir' in content.lower() or 'no incluir' in content.lower(), "No security warning found"
        
        print("  ✓ Security warnings present")
        
        # Check for features mentioned in requirements
        assert 'dry_run' in content.lower() or 'dry run' in content.lower(), "Dry-run feature not found"
        assert 'backup' in content.lower(), "Backup feature not found"
        assert 'progress' in content.lower(), "Progress tracking not found"
        assert 'log' in content.lower(), "Logging not found"
        
        print("  ✓ All required features present")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def test_menu_integration():
    """Test that the menu integration is correct"""
    print("\nTest: Menu integration in app_gui_qt.py...")
    
    try:
        app_gui_path = os.path.join(os.path.dirname(__file__), 'app_gui_qt.py')
        
        with open(app_gui_path, 'r') as f:
            content = f.read()
        
        # Check menu item
        assert 'Migrar a Firebase' in content, "Migration menu item not found"
        assert '_abrir_dialogo_migracion_firebase' in content, "Menu action method not found"
        
        print("  ✓ Menu item 'Migrar a Firebase' found")
        
        # Check method definition
        assert 'def _abrir_dialogo_migracion_firebase' in content, "Method definition not found"
        assert 'DialogoMigracionFirebase' in content, "Dialog import/usage not found"
        
        print("  ✓ Method _abrir_dialogo_migracion_firebase defined")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def test_package_structure():
    """Test that package structure is correct"""
    print("\nTest: Package structure...")
    
    try:
        # Check directories
        dirs_to_check = [
            'app',
            'app/ui',
            'app/ui/dialogs'
        ]
        
        for dir_path in dirs_to_check:
            full_path = os.path.join(os.path.dirname(__file__), dir_path)
            assert os.path.isdir(full_path), f"Directory not found: {dir_path}"
            print(f"  ✓ Directory exists: {dir_path}")
        
        # Check __init__ files
        init_files = [
            'app/__init__.py',
            'app/ui/__init__.py',
            'app/ui/dialogs/__init__.py'
        ]
        
        for init_file in init_files:
            full_path = os.path.join(os.path.dirname(__file__), init_file)
            assert os.path.exists(full_path), f"__init__ file not found: {init_file}"
            print(f"  ✓ __init__ file exists: {init_file}")
        
        # Check DialogoMigracionFirebase is exported
        dialogs_init = os.path.join(os.path.dirname(__file__), 'app/ui/dialogs/__init__.py')
        with open(dialogs_init, 'r') as f:
            content = f.read()
        
        assert 'DialogoMigracionFirebase' in content, "DialogoMigracionFirebase not exported"
        print("  ✓ DialogoMigracionFirebase exported from package")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def test_gitignore_updated():
    """Test that .gitignore includes necessary rules"""
    print("\nTest: .gitignore updated...")
    
    try:
        gitignore_path = os.path.join(os.path.dirname(__file__), '.gitignore')
        
        with open(gitignore_path, 'r') as f:
            content = f.read()
        
        # Check for important exclusions
        required_patterns = [
            'serviceAccount.json',
            'backups/',
            'mapping*.json',
            'migration_log*.txt'
        ]
        
        for pattern in required_patterns:
            assert pattern in content, f"Pattern not found in .gitignore: {pattern}"
            print(f"  ✓ .gitignore includes: {pattern}")
        
        return True
        
    except Exception as e:
        print(f"  ✗ Error: {e}")
        return False


def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("Testing Firebase Migration UI (PR4)")
    print("=" * 60)
    
    tests = [
        test_dialog_structure,
        test_menu_integration,
        test_package_structure,
        test_gitignore_updated
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
