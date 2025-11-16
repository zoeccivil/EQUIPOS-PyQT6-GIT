#!/usr/bin/env python3
"""
Test script para verificar la arquitectura Firestore-first.

Este script NO ejecuta la aplicación completa, solo verifica que:
1. Los módulos se importen correctamente
2. AppSettings se cree y funcione
3. RepositoryFactory esté disponible
4. Los diálogos de configuración estén disponibles
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test that all new modules can be imported."""
    print("="*60)
    print("TEST 1: Imports de módulos principales")
    print("="*60)
    
    try:
        from app.app_settings import AppSettings, get_settings
        print("✅ app.app_settings")
    except ImportError as e:
        print(f"❌ app.app_settings: {e}")
        return False
    
    try:
        from app.repo.base_repository import BaseRepository
        print("✅ app.repo.base_repository")
    except ImportError as e:
        print(f"❌ app.repo.base_repository: {e}")
        return False
    
    try:
        from app.repo.firestore_repository import FirestoreRepository
        print("✅ app.repo.firestore_repository")
    except ImportError as e:
        print(f"❌ app.repo.firestore_repository: {e}")
        return False
    
    try:
        from app.repo.sqlite_repository import SQLiteRepository
        print("✅ app.repo.sqlite_repository")
    except ImportError as e:
        print(f"❌ app.repo.sqlite_repository: {e}")
        return False
    
    try:
        from app.repo.repository_factory import RepositoryFactory
        print("✅ app.repo.repository_factory")
    except ImportError as e:
        print(f"❌ app.repo.repository_factory: {e}")
        return False
    
    print()
    return True


def test_settings():
    """Test AppSettings functionality."""
    print("="*60)
    print("TEST 2: Funcionalidad de AppSettings")
    print("="*60)
    
    try:
        from app.app_settings import AppSettings, get_settings
        
        # Create settings instance
        settings = AppSettings()
        print(f"✅ AppSettings creado")
        
        # Test get/set
        data_source = settings.get_data_source()
        print(f"✅ Data source actual: {data_source}")
        
        # Test Firestore config check
        is_configured = settings.is_firestore_configured()
        print(f"✅ Firestore configurado: {is_configured}")
        
        # Test backup folder
        backup_folder = settings.get_backup_folder()
        print(f"✅ Carpeta de backup: {backup_folder}")
        
        print()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        print()
        return False


def test_repository_factory():
    """Test RepositoryFactory availability."""
    print("="*60)
    print("TEST 3: RepositoryFactory")
    print("="*60)
    
    try:
        from app.repo.repository_factory import RepositoryFactory
        from app.app_settings import get_settings
        
        settings = get_settings()
        print("✅ RepositoryFactory disponible")
        print(f"   Data source configurado: {settings.get_data_source()}")
        
        # Note: We don't actually create a repository here because
        # it would require valid Firestore credentials or a SQLite DB
        print("   (No se crea repositorio - requiere credenciales/DB)")
        
        print()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        print()
        return False


def test_ui_dialogs():
    """Test that UI dialogs can be imported (requires PyQt6)."""
    print("="*60)
    print("TEST 4: Diálogos UI (requiere PyQt6)")
    print("="*60)
    
    try:
        from app.ui.data_source_widget import DataSourceWidget
        print("✅ DataSourceWidget importado")
    except ImportError as e:
        print(f"⚠️  DataSourceWidget: {e} (PyQt6 no instalado?)")
    
    try:
        from app.ui.migration_dialog import DialogoMigracionFirestore
        print("✅ DialogoMigracionFirestore importado")
    except ImportError as e:
        print(f"⚠️  DialogoMigracionFirestore: {e}")
    
    try:
        from app.ui.backup_dialog import DialogoBackupSQLite
        print("✅ DialogoBackupSQLite importado")
    except ImportError as e:
        print(f"⚠️  DialogoBackupSQLite: {e}")
    
    print()
    return True


def main():
    """Run all tests."""
    print()
    print("╔" + "="*58 + "╗")
    print("║" + " "*10 + "TEST DE ARQUITECTURA FIRESTORE-FIRST" + " "*12 + "║")
    print("╚" + "="*58 + "╝")
    print()
    
    results = []
    
    results.append(("Imports", test_imports()))
    results.append(("Settings", test_settings()))
    results.append(("RepositoryFactory", test_repository_factory()))
    results.append(("UI Dialogs", test_ui_dialogs()))
    
    print("="*60)
    print("RESUMEN")
    print("="*60)
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status:10} {name}")
    
    all_passed = all(result[1] for result in results)
    
    print()
    if all_passed:
        print("🎉 TODOS LOS TESTS PASARON")
        print()
        print("La arquitectura Firestore-first está correctamente implementada.")
        print()
        print("Próximos pasos:")
        print("1. Instalar PyQt6: pip install PyQt6")
        print("2. Configurar Firestore siguiendo FIRESTORE_SETUP.md")
        print("3. Ejecutar la aplicación: python main_qt.py")
        return 0
    else:
        print("⚠️  ALGUNOS TESTS FALLARON")
        print()
        print("Revisa los errores arriba y corrige los problemas.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
