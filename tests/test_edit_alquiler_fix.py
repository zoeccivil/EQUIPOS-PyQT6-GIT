"""
Manual test script for edit alquiler fix.
This script verifies that editing a rental doesn't create a duplicate.

To run this test:
1. Ensure you have a test database with at least one rental transaction
2. Run: python tests/test_edit_alquiler_fix.py
3. Verify that editing doesn't create duplicates

Note: This is a manual verification test, not automated.
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from logic import DatabaseManager
import tempfile
import uuid


def test_edit_alquiler_no_duplicate():
    """
    Test that editing an alquiler updates the existing record instead of creating a duplicate.
    """
    print("=" * 70)
    print("Testing: Edit Alquiler - No Duplicate Creation")
    print("=" * 70)
    
    # Create temporary database
    temp_db = tempfile.NamedTemporaryFile(mode='w', suffix='.db', delete=False)
    temp_db.close()
    db_path = temp_db.name
    
    try:
        # Initialize database
        db = DatabaseManager(db_path)
        db.crear_tablas_nucleo()
        db.asegurar_tabla_alquiler_meta()
        
        # Create a test project
        db.execute("INSERT INTO proyectos (id, nombre, cuenta_principal) VALUES (?, ?, ?)", 
                   (8, "Test Project", "Test Account"))
        
        # Create test account
        db.execute("INSERT INTO cuentas (id, nombre, tipo_cuenta) VALUES (?, ?, ?)",
                   (1, "Test Account", "General"))
        
        # Create test category
        db.execute("INSERT INTO categorias (id, nombre) VALUES (?, ?)",
                   (1, "ALQUILERES"))
        
        # Create test equipment
        db.execute("INSERT INTO equipos (id, proyecto_id, nombre, activo) VALUES (?, ?, ?, ?)",
                   (1, 8, "Test Equipment", 1))
        
        # Create test entities table
        db.execute("""
            CREATE TABLE IF NOT EXISTS equipos_entidades (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT NOT NULL,
                tipo TEXT NOT NULL,
                proyecto_id INTEGER,
                activo INTEGER DEFAULT 1
            )
        """)
        
        # Create test client and operator
        db.execute("INSERT INTO equipos_entidades (id, nombre, tipo, proyecto_id, activo) VALUES (?, ?, ?, ?, ?)",
                   (1, "Test Client", "Cliente", 8, 1))
        db.execute("INSERT INTO equipos_entidades (id, nombre, tipo, proyecto_id, activo) VALUES (?, ?, ?, ?, ?)",
                   (2, "Test Operator", "Operador", 8, 1))
        
        # Create initial rental transaction
        transaction_id = uuid.uuid4().hex
        initial_data = {
            'id': transaction_id,
            'proyecto_id': 8,
            'cuenta_id': 1,
            'categoria_id': 1,
            'tipo': 'Ingreso',
            'descripcion': 'Test Rental',
            'monto': 1000.0,
            'fecha': '2024-01-01',
            'cliente_id': 1,
            'operador_id': 2,
            'equipo_id': 1,
            'conduce': 'TEST-001',
            'ubicacion': 'Test Location',
            'horas': 10.0,
            'precio_por_hora': 100.0,
            'pagado': 0
        }
        
        query = """
            INSERT INTO transacciones 
            (id, proyecto_id, cuenta_id, categoria_id, tipo, descripcion, monto, fecha,
             cliente_id, operador_id, equipo_id, conduce, ubicacion, horas, precio_por_hora, pagado)
            VALUES 
            (:id, :proyecto_id, :cuenta_id, :categoria_id, :tipo, :descripcion, :monto, :fecha,
             :cliente_id, :operador_id, :equipo_id, :conduce, :ubicacion, :horas, :precio_por_hora, :pagado)
        """
        db.execute(query, initial_data)
        
        print(f"\n1. Created initial rental with ID: {transaction_id}")
        
        # Count transactions before edit
        count_before = db.fetchone("SELECT COUNT(*) as count FROM transacciones WHERE proyecto_id = 8")['count']
        print(f"2. Transaction count before edit: {count_before}")
        
        # Simulate edit: get details
        detalles = db.obtener_detalles_alquiler(transaction_id)
        print(f"3. Retrieved rental details: ID={detalles.get('id')}, Conduce={detalles.get('conduce')}")
        
        # Check that details have 'id'
        assert detalles.get('id') == transaction_id, "Details missing transaction ID!"
        
        # Simulate edit: update data
        updated_data = {
            'monto': 1200.0,
            'horas': 12.0,
            'conduce': 'TEST-001-UPDATED',
            'ubicacion': 'Updated Location'
        }
        
        success = db.actualizar_alquiler(transaction_id, updated_data)
        print(f"4. Update result: {success}")
        
        # Count transactions after edit
        count_after = db.fetchone("SELECT COUNT(*) as count FROM transacciones WHERE proyecto_id = 8")['count']
        print(f"5. Transaction count after edit: {count_after}")
        
        # Verify no duplicate was created
        if count_before == count_after:
            print("\n✅ TEST PASSED: No duplicate created during edit")
        else:
            print(f"\n❌ TEST FAILED: Duplicate created! Count before: {count_before}, after: {count_after}")
            return False
        
        # Verify the transaction was actually updated
        updated_details = db.obtener_detalles_alquiler(transaction_id)
        if updated_details.get('conduce') == 'TEST-001-UPDATED':
            print("✅ TEST PASSED: Transaction was updated correctly")
        else:
            print(f"❌ TEST FAILED: Transaction not updated. Conduce: {updated_details.get('conduce')}")
            return False
        
        print("\n" + "=" * 70)
        print("ALL TESTS PASSED ✅")
        print("=" * 70)
        return True
        
    except Exception as e:
        print(f"\n❌ TEST FAILED with exception: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    finally:
        # Cleanup
        if os.path.exists(db_path):
            os.unlink(db_path)
            print(f"\nCleaned up temporary database: {db_path}")


if __name__ == "__main__":
    success = test_edit_alquiler_no_duplicate()
    sys.exit(0 if success else 1)
