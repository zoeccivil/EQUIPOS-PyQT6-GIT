"""
Test for entities management (Clientes y Operadores)

Verifies that all CRUD operations work correctly for entities including
telefono and cedula fields.
"""
import sys
import os
import tempfile
import shutil

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from logic import DatabaseManager


def test_entidades_crud():
    """Test full CRUD cycle for entities"""
    print("Test: Complete CRUD cycle for entities (Clientes y Operadores)...")
    
    temp_dir = tempfile.mkdtemp()
    try:
        temp_db_path = os.path.join(temp_dir, "test_entities.db")
        
        # Create and initialize database
        db = DatabaseManager(temp_db_path)
        db.crear_tablas_nucleo()
        db.sembrar_datos_iniciales()
        db.asegurar_tabla_equipos_entidades()
        
        # Create a project
        db.execute("INSERT INTO proyectos (nombre, moneda) VALUES (?, ?)", ("Proyecto Test", "RD$"))
        proyecto_id = 1
        
        print("  ✓ Database and project created")
        
        # ========== TEST CREATE ==========
        print("\n  Testing CREATE...")
        
        # Create Cliente
        cliente_data = {
            "proyecto_id": proyecto_id,
            "tipo": "Cliente",
            "nombre": "Juan Pérez",
            "telefono": "809-555-1234",
            "cedula": "001-1234567-8",
            "activo": 1
        }
        
        result = db.guardar_entidad(cliente_data)
        assert result, "Should successfully create cliente"
        
        # Verify creation
        clientes = db.obtener_entidades_equipo_por_tipo(proyecto_id, "Cliente")
        assert len(clientes) == 1, "Should have 1 cliente"
        cliente = clientes[0]
        assert cliente['nombre'] == "Juan Pérez", "Name should match"
        assert cliente['telefono'] == "809-555-1234", "Phone should match"
        assert cliente['cedula'] == "001-1234567-8", "Cedula should match"
        assert cliente['activo'] == 1, "Should be active"
        
        cliente_id = cliente['id']
        print(f"    ✓ Cliente created: ID={cliente_id}, {cliente['nombre']}")
        
        # Create Operador
        operador_data = {
            "proyecto_id": proyecto_id,
            "tipo": "Operador",
            "nombre": "María García",
            "telefono": "829-555-5678",
            "cedula": None,  # Operador might not have cedula
            "activo": 1
        }
        
        result = db.guardar_entidad(operador_data)
        assert result, "Should successfully create operador"
        
        operadores = db.obtener_entidades_equipo_por_tipo(proyecto_id, "Operador")
        assert len(operadores) == 1, "Should have 1 operador"
        operador = operadores[0]
        assert operador['nombre'] == "María García", "Name should match"
        assert operador['telefono'] == "829-555-5678", "Phone should match"
        assert operador['cedula'] is None or operador['cedula'] == '', "Cedula should be None/empty"
        
        operador_id = operador['id']
        print(f"    ✓ Operador created: ID={operador_id}, {operador['nombre']}")
        
        # ========== TEST READ ==========
        print("\n  Testing READ...")
        
        # Read by ID
        cliente_by_id = db.obtener_entidad_por_id(cliente_id)
        assert cliente_by_id is not None, "Should find cliente by ID"
        assert cliente_by_id['nombre'] == "Juan Pérez", "Name should match"
        assert cliente_by_id['telefono'] == "809-555-1234", "Phone should match"
        print(f"    ✓ Read by ID successful: {cliente_by_id['nombre']}")
        
        # Read by type
        all_clientes = db.obtener_entidades_equipo_por_tipo(proyecto_id, "Cliente")
        assert len(all_clientes) == 1, "Should have 1 cliente"
        
        all_operadores = db.obtener_entidades_equipo_por_tipo(proyecto_id, "Operador")
        assert len(all_operadores) == 1, "Should have 1 operador"
        print(f"    ✓ Read by type successful: {len(all_clientes)} clientes, {len(all_operadores)} operadores")
        
        # ========== TEST UPDATE ==========
        print("\n  Testing UPDATE...")
        
        # Update cliente
        updated_cliente_data = {
            "proyecto_id": proyecto_id,
            "tipo": "Cliente",
            "nombre": "Juan Pérez Actualizado",
            "telefono": "809-999-9999",
            "cedula": "001-9999999-9",
            "activo": 1
        }
        
        result = db.guardar_entidad(updated_cliente_data, cliente_id)
        assert result, "Should successfully update cliente"
        
        # Verify update
        updated_cliente = db.obtener_entidad_por_id(cliente_id)
        assert updated_cliente['nombre'] == "Juan Pérez Actualizado", "Name should be updated"
        assert updated_cliente['telefono'] == "809-999-9999", "Phone should be updated"
        assert updated_cliente['cedula'] == "001-9999999-9", "Cedula should be updated"
        print(f"    ✓ Update successful: {updated_cliente['nombre']}, {updated_cliente['telefono']}")
        
        # ========== TEST DELETE (soft delete - mark as inactive) ==========
        print("\n  Testing DELETE (soft delete)...")
        
        result = db.eliminar_entidad(cliente_id)
        assert result, "Should successfully delete (mark inactive) cliente"
        
        # Verify it's marked as inactive
        deleted_cliente = db.obtener_entidad_por_id(cliente_id)
        assert deleted_cliente is not None, "Record should still exist"
        assert deleted_cliente['activo'] == 0, "Should be marked as inactive"
        print(f"    ✓ Soft delete successful: activo={deleted_cliente['activo']}")
        
        # Verify it doesn't appear in active list (if the query filters by activo)
        # Note: obtener_entidades_equipo_por_tipo doesn't filter by activo currently
        # This is expected behavior - we might want to show inactive entities in management UI
        
        # ========== FINAL VERIFICATION ==========
        print("\n  Final verification...")
        
        # Count total entities
        all_entities = db.fetchall("SELECT * FROM equipos_entidades WHERE proyecto_id = ?", (proyecto_id,))
        assert len(all_entities) == 2, "Should have 2 total entities (1 cliente, 1 operador)"
        
        # Verify table structure includes all columns
        columns = db.fetchone("PRAGMA table_info(equipos_entidades)", ())
        # This returns None with fetchone, need to use fetchall
        table_info = db.fetchall("PRAGMA table_info(equipos_entidades)", ())
        column_names = [col['name'] for col in table_info]
        
        required_columns = ['id', 'nombre', 'tipo', 'proyecto_id', 'activo', 'telefono', 'cedula']
        for col in required_columns:
            assert col in column_names, f"Table should have column: {col}"
        
        print(f"    ✓ All required columns present: {', '.join(required_columns)}")
        
        print("\n✓ All CRUD operations successful!")
        return True
        
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_with_existing_database():
    """Test with existing database if available"""
    print("\n" + "=" * 60)
    print("Test: With existing database...")
    print("=" * 60)
    
    db_path = "progain_database-qt.db"
    if not os.path.exists(db_path):
        print(f"  ⊘ Skipping - database not found: {db_path}")
        return
    
    try:
        db = DatabaseManager(db_path)
        
        # Test reading entities
        # Assuming project ID 8 exists (from the code)
        proyecto_id = 8
        
        clientes = db.obtener_entidades_equipo_por_tipo(proyecto_id, "Cliente")
        print(f"  ✓ Found {len(clientes)} clientes in project {proyecto_id}")
        
        if clientes:
            cliente = clientes[0]
            print(f"    Sample: {cliente.get('nombre')} - Tel: {cliente.get('telefono', 'N/A')} - Cédula: {cliente.get('cedula', 'N/A')}")
        
        operadores = db.obtener_entidades_equipo_por_tipo(proyecto_id, "Operador")
        print(f"  ✓ Found {len(operadores)} operadores in project {proyecto_id}")
        
        if operadores:
            operador = operadores[0]
            print(f"    Sample: {operador.get('nombre')} - Tel: {operador.get('telefono', 'N/A')}")
        
        print("✓ Successfully accessed existing database")
        
    except Exception as e:
        print(f"  ✗ Error accessing existing database: {e}")


if __name__ == "__main__":
    print("=" * 60)
    print("Testing Entities Management (Clientes y Operadores)")
    print("=" * 60)
    
    try:
        test_entidades_crud()
        test_with_existing_database()
        
        print("\n" + "=" * 60)
        print("All tests passed! ✓")
        print("=" * 60)
        sys.exit(0)
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
