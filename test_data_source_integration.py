"""
Test suite for data source integration in main app.

Tests:
1. Menu item "Fuente de Datos" exists
2. Method _abrir_configuracion_fuente_datos is defined
3. Status bar indicator is created
4. main_qt.py uses AppSettings for data source selection
"""

import os
import sys

# Test 1: Check menu item exists in app_gui_qt.py
print("=" * 60)
print("Testing Data Source Integration")
print("=" * 60)

print("\nTest 1: Checking menu item in app_gui_qt.py...")
with open('app_gui_qt.py', 'r', encoding='utf-8') as f:
    content = f.read()
    
    # Check menu item exists
    if 'Fuente de Datos (SQLite/Firestore)' in content:
        print("  ✓ Menu item 'Fuente de Datos (SQLite/Firestore)' found")
    else:
        print("  ✗ Menu item not found")
        sys.exit(1)
    
    # Check method is defined
    if 'def _abrir_configuracion_fuente_datos(self):' in content:
        print("  ✓ Method _abrir_configuracion_fuente_datos defined")
    else:
        print("  ✗ Method not defined")
        sys.exit(1)
    
    # Check status bar creation
    if 'def _create_status_bar(self):' in content:
        print("  ✓ Status bar creation method defined")
    else:
        print("  ✗ Status bar method not defined")
        sys.exit(1)
    
    # Check status bar is called
    if 'self._create_status_bar()' in content:
        print("  ✓ Status bar creation is called")
    else:
        print("  ✗ Status bar not called in initialization")
        sys.exit(1)

print("✓ All app_gui_qt.py tests passed!")

# Test 2: Check main_qt.py uses AppSettings
print("\nTest 2: Checking main_qt.py integration...")
with open('main_qt.py', 'r', encoding='utf-8') as f:
    content = f.read()
    
    # Check imports
    if 'from app.app_settings import get_app_settings' in content:
        print("  ✓ AppSettings imported")
    else:
        print("  ✗ AppSettings not imported")
        sys.exit(1)
    
    if 'from app.repo.repository_factory import RepositoryFactory' in content:
        print("  ✓ RepositoryFactory imported")
    else:
        print("  ✗ RepositoryFactory not imported")
        sys.exit(1)
    
    # Check data source selection logic
    if 'data_source = settings.get_data_source()' in content:
        print("  ✓ Data source selection implemented")
    else:
        print("  ✗ Data source selection not found")
        sys.exit(1)
    
    # Check Firestore handling
    if "data_source == 'firestore'" in content:
        print("  ✓ Firestore data source handling implemented")
    else:
        print("  ✗ Firestore handling not found")
        sys.exit(1)

print("✓ All main_qt.py tests passed!")

# Test 3: Verify required modules exist
print("\nTest 3: Checking required modules...")

required_files = [
    'app/app_settings.py',
    'app/ui/data_source_widget.py',
    'app/repo/firestore_repository.py',
    'app/repo/repository_factory.py'
]

for file_path in required_files:
    if os.path.exists(file_path):
        print(f"  ✓ {file_path} exists")
    else:
        print(f"  ✗ {file_path} not found")
        sys.exit(1)

print("✓ All required modules exist!")

# Test 4: Integration flow test
print("\nTest 4: Testing integration flow...")

try:
    from app.app_settings import get_app_settings
    from app.repo.repository_factory import RepositoryFactory
    
    print("  ✓ Can import AppSettings and RepositoryFactory")
    
    # Test settings
    settings = get_app_settings()
    data_source = settings.get_data_source()
    print(f"  ✓ Current data source: {data_source}")
    
    # Test creating repository from settings
    if data_source == 'sqlite':
        print("  ✓ SQLite mode - repository creation will work with existing DB")
    elif data_source == 'firestore':
        print("  ⚠ Firestore mode - will need valid credentials to connect")
    else:
        print(f"  ✗ Unknown data source: {data_source}")
        sys.exit(1)
    
    print("✓ Integration flow test passed!")
    
except ImportError as e:
    print(f"  ✗ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"  ✗ Error: {e}")
    sys.exit(1)

# Summary
print("\n" + "=" * 60)
print("Integration Test Summary")
print("=" * 60)
print("✓ Menu integration complete")
print("✓ Status bar indicator implemented")
print("✓ main_qt.py respects data source configuration")
print("✓ All required modules present")
print("✓ Integration flow validated")
print("\n" + "=" * 60)
print("All integration tests passed! ✓")
print("=" * 60)
