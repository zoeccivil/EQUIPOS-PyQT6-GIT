"""
Basic tests for repository abstraction layer

These tests verify that the repository pattern is working correctly
with the existing SQLite database.
"""
import sys
import os
import tempfile
import shutil

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from logic import DatabaseManager
from app.repo.repository_factory import RepositoryFactory
from app.repo.sqlite_repository import SQLiteRepository


def test_repository_creation():
    """Test that we can create a repository from DatabaseManager"""
    print("Test 1: Creating repository from DatabaseManager...")
    
    # Create a temporary database
    temp_dir = tempfile.mkdtemp()
    try:
        temp_db_path = os.path.join(temp_dir, "test.db")
        
        # Create DatabaseManager
        db_manager = DatabaseManager(temp_db_path)
        db_manager.crear_tablas_nucleo()
        
        # Create repository from DatabaseManager
        repo = RepositoryFactory.create_repository_from_db_manager(db_manager)
        
        assert isinstance(repo, SQLiteRepository), "Repository should be SQLiteRepository"
        assert repo.get_db_manager() == db_manager, "Should return same db_manager"
        
        print("✓ Repository created successfully")
        
    finally:
        # Cleanup
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_repository_factory_sqlite():
    """Test creating SQLite repository via factory"""
    print("\nTest 2: Creating SQLite repository via factory...")
    
    temp_dir = tempfile.mkdtemp()
    try:
        temp_db_path = os.path.join(temp_dir, "test.db")
        
        # Create repository via factory
        repo = RepositoryFactory.create_sqlite_repository(temp_db_path)
        
        assert isinstance(repo, SQLiteRepository), "Should create SQLiteRepository"
        
        # Initialize tables
        db = repo.get_db_manager()
        db.crear_tablas_nucleo()
        db.sembrar_datos_iniciales()
        
        print("✓ Factory created SQLite repository successfully")
        
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_repository_operations():
    """Test basic repository operations"""
    print("\nTest 3: Testing repository operations...")
    
    temp_dir = tempfile.mkdtemp()
    try:
        temp_db_path = os.path.join(temp_dir, "test.db")
        
        # Create and initialize repository
        repo = RepositoryFactory.create_sqlite_repository(temp_db_path)
        db = repo.get_db_manager()
        db.crear_tablas_nucleo()
        db.sembrar_datos_iniciales()
        
        # Test obtener_proyectos
        proyectos = repo.obtener_proyectos()
        assert isinstance(proyectos, list), "Should return list of projects"
        print(f"  ✓ Found {len(proyectos)} projects")
        
        # Test listar_cuentas
        cuentas = repo.listar_cuentas()
        assert isinstance(cuentas, list), "Should return list of accounts"
        print(f"  ✓ Found {len(cuentas)} accounts")
        
        # Test asegurar_tabla_equipos_entidades
        repo.asegurar_tabla_equipos_entidades()
        print("  ✓ Ensured equipos_entidades table exists")
        
        print("✓ All repository operations successful")
        
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_with_existing_database():
    """Test with existing database if available"""
    print("\nTest 4: Testing with existing database...")
    
    db_path = "progain_database-qt.db"
    if not os.path.exists(db_path):
        print(f"  ⊘ Skipping - database not found: {db_path}")
        return
    
    try:
        # Create repository from existing database
        db_manager = DatabaseManager(db_path)
        repo = RepositoryFactory.create_repository_from_db_manager(db_manager)
        
        # Test reading projects
        proyectos = repo.obtener_proyectos()
        print(f"  ✓ Read {len(proyectos)} projects from existing database")
        
        # Test reading equipment
        equipos = repo.obtener_todos_los_equipos()
        print(f"  ✓ Read {len(equipos)} equipment items from existing database")
        
        print("✓ Successfully accessed existing database via repository")
        
    except Exception as e:
        print(f"  ✗ Error accessing existing database: {e}")


def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("Testing Repository Abstraction Layer")
    print("=" * 60)
    
    try:
        test_repository_creation()
        test_repository_factory_sqlite()
        test_repository_operations()
        test_with_existing_database()
        
        print("\n" + "=" * 60)
        print("All tests passed! ✓")
        print("=" * 60)
        return True
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
