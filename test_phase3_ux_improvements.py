"""
Test suite for Phase 3 UX/UI improvements.

Tests keyboard shortcuts, table models, and dashboard components.
"""

import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def test_shortcuts_system():
    """Test keyboard shortcuts manager."""
    print("Test 1: Shortcuts System")
    
    # Test file exists
    shortcuts_file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'app', 'ui', 'shortcuts.py'
    )
    
    if not os.path.exists(shortcuts_file):
        print(f"  ✗ shortcuts.py not found: {shortcuts_file}")
        return False
    
    print(f"  ✓ shortcuts.py exists")
    
    # Test file contains expected content
    with open(shortcuts_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    if 'ShortcutsManager' not in content:
        print("  ✗ ShortcutsManager class not found")
        return False
    print("  ✓ ShortcutsManager class found")
    
    if 'GLOBAL_SHORTCUTS' not in content:
        print("  ✗ GLOBAL_SHORTCUTS not defined")
        return False
    print("  ✓ GLOBAL_SHORTCUTS defined")
    
    if 'TABLE_SHORTCUTS' not in content:
        print("  ✗ TABLE_SHORTCUTS not defined")
        return False
    print("  ✓ TABLE_SHORTCUTS defined")
    
    print("✓ Shortcuts system tests passed!\n")
    return True


def test_table_models_structure():
    """Test table models package structure."""
    print("Test 2: Table Models Structure")
    
    # Test models package exists
    models_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'app', 'ui', 'models'
    )
    
    if os.path.exists(models_path):
        print(f"  ✓ Models package exists")
    else:
        print(f"  ✗ Models package not found: {models_path}")
        return False
    
    # Test __init__.py exists
    init_file = os.path.join(models_path, '__init__.py')
    if os.path.exists(init_file):
        print("  ✓ __init__.py exists")
    else:
        print("  ✗ __init__.py not found")
        return False
    
    print("✓ Table models structure validated!\n")
    return True


def test_shortcuts_functionality():
    """Test shortcuts functionality."""
    print("Test 3: Shortcuts Functionality")
    
    # Read shortcuts file
    shortcuts_file = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'app', 'ui', 'shortcuts.py'
    )
    
    with open(shortcuts_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Test that expected functions are defined
    expected_functions = ['get_shortcuts_help_text', 'copy_table_selection_as_csv']
    for func in expected_functions:
        if f'def {func}' not in content:
            print(f"  ✗ Function {func} not found")
            return False
    print(f"  ✓ All {len(expected_functions)} expected functions defined")
    
    # Test that all expected shortcuts are mentioned
    expected_shortcuts = ['Ctrl+N', 'Ctrl+E', 'Del', 'Ctrl+S', 'F5']
    for shortcut in expected_shortcuts:
        if shortcut not in content:
            print(f"  ✗ Shortcut {shortcut} not defined")
            return False
    print(f"  ✓ All {len(expected_shortcuts)} expected shortcuts defined")
    
    print("✓ Shortcuts functionality tests passed!\n")
    return True


def test_documentation_exists():
    """Test that documentation files exist."""
    print("Test 4: Documentation")
    
    docs_dir = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        'docs'
    )
    
    # Test summary doc
    summary_file = os.path.join(docs_dir, 'PHASE3_IMPLEMENTATION_SUMMARY.md')
    if os.path.exists(summary_file):
        print(f"  ✓ Implementation summary exists")
    else:
        print(f"  ⚠ Implementation summary not found (optional)")
    
    print("✓ Documentation check complete!\n")
    return True


def main():
    """Run all Phase 3 tests."""
    print("=" * 60)
    print("Testing Phase 3: UX/UI Improvements")
    print("=" * 60)
    print()
    
    tests = [
        test_shortcuts_system,
        test_table_models_structure,
        test_shortcuts_functionality,
        test_documentation_exists,
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"✗ Test failed with exception: {e}\n")
            results.append(False)
    
    print("=" * 60)
    print("Test Summary")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    print(f"Passed: {passed}/{total}")
    
    if all(results):
        print("\n✓ All Phase 3 tests passed!")
        return True
    else:
        print(f"\n✗ {total - passed} test(s) failed")
        return False


if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
