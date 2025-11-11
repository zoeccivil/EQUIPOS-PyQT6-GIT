"""
Test suite for Phase 2: Theme System Integration
"""

import os
import sys

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_theme_files():
    """Test that all theme files exist and have required attributes"""
    print("\nTest 1: Theme files validation")
    
    theme_dir = 'app/ui/themes'
    theme_files = [f for f in os.listdir(theme_dir) if f.endswith('_theme.py')]
    
    print(f"  ✓ Found {len(theme_files)} theme files")
    
    for theme_file in theme_files:
        filepath = os.path.join(theme_dir, theme_file)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for required attributes
        assert 'THEME_STYLESHEET' in content, f"{theme_file} missing THEME_STYLESHEET"
        assert 'THEME_METADATA' in content, f"{theme_file} missing THEME_METADATA"
        
        # Check metadata fields exist
        assert "'name':" in content, f"{theme_file} metadata missing 'name'"
        assert "'description':" in content, f"{theme_file} metadata missing 'description'"
        assert "'type':" in content, f"{theme_file} metadata missing 'type'"
        
        print(f"  ✓ {theme_file} validated")
    
    print("✓ All theme files validated!")


def test_theme_manager():
    """Test theme manager functions"""
    print("\nTest 2: Theme manager")
    
    # Check file exists and has required functions
    with open('app/ui/themes/theme_manager.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    assert 'def list_themes' in content, "Theme manager missing list_themes"
    assert 'def apply_theme' in content, "Theme manager missing apply_theme"
    assert 'def get_current_theme' in content, "Theme manager missing get_current_theme"
    assert 'def apply_theme_from_settings' in content, "Theme manager missing apply_theme_from_settings"
    print("  ✓ Theme manager has all required functions")
    
    print("✓ Theme manager tests passed!")


def test_theme_utils():
    """Test theme utility functions"""
    print("\nTest 3: Theme utils")
    
    with open('app/ui/themes/theme_utils.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    assert 'def adjust_color' in content, "Theme utils missing adjust_color"
    assert 'def get_status_color' in content, "Theme utils missing get_status_color"
    assert 'def get_theme_colors' in content, "Theme utils missing get_theme_colors"
    assert 'def is_dark_theme' in content, "Theme utils missing is_dark_theme"
    print("  ✓ Theme utils has all required functions")
    
    print("✓ Theme utils tests passed!")


def test_icon_loader():
    """Test icon loader"""
    print("\nTest 4: Icon loader")
    
    with open('app/ui/icons/icon_loader.py', 'r', encoding='utf-8') as f:
        content = f.read()
    
    assert 'def get_icon' in content, "Icon loader missing get_icon"
    assert 'ICON_MAP' in content, "Icon loader missing ICON_MAP"
    
    # Count icons in ICON_MAP
    icon_count = content.count("':")
    assert icon_count >= 40, f"ICON_MAP should have 40+ icons, found ~{icon_count}"
    print(f"  ✓ Icon loader has all required functions and ~{icon_count} icons")
    
    print("✓ Icon loader tests passed!")


def test_menu_integration():
    """Test menu integration in main app"""
    print("\nTest 5: Menu integration")
    
    app_gui_path = 'app_gui_qt.py'
    
    if os.path.exists(app_gui_path):
        with open(app_gui_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Check for theme menu creation
        assert '_create_theme_menu' in content, \
            "app_gui_qt.py should have _create_theme_menu method"
        print("  ✓ app_gui_qt.py has theme menu creation")
        
        # Check for theme change method
        assert '_cambiar_tema' in content, \
            "app_gui_qt.py should have _cambiar_tema method"
        print("  ✓ app_gui_qt.py has theme change method")
        
        # Check for startup theme application
        assert '_apply_saved_theme' in content, \
            "app_gui_qt.py should have _apply_saved_theme method"
        print("  ✓ Startup theme application implemented")
        
        # Check for Apariencia menu
        assert 'Apariencia' in content, \
            "app_gui_qt.py should have Apariencia menu"
        print("  ✓ Apariencia menu added")
        
    else:
        print("  ⚠ app_gui_qt.py not found")
        raise FileNotFoundError("app_gui_qt.py not found")
    
    print("✓ Menu integration verified!")


if __name__ == '__main__':
    print("=" * 60)
    print("Testing Phase 2: Theme System Integration")
    print("=" * 60)
    
    try:
        test_theme_files()
        test_theme_manager()
        test_theme_utils()
        test_icon_loader()
        test_menu_integration()
        
        print("\n" + "=" * 60)
        print("All Phase 2 tests passed! ✓")
        print("=" * 60)
        
    except Exception as e:
        print("\n" + "=" * 60)
        print(f"Tests failed: {e}")
        print("=" * 60)
        sys.exit(1)
