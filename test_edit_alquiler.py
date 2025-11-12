"""
Test for alquiler edit fix

Verifies that editing an alquiler updates both transacciones and equipos_alquiler_meta tables.
"""
import sys
import os
import tempfile
import shutil
import uuid

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from logic import DatabaseManager


def test_actualizar_alquiler_updates_both_tables():
    """Test that actualizar_alquiler updates both tables correctly"""
    print("Test: Actualizar alquiler updates both transacciones and equipos_alquiler_meta...")
    
    temp_dir = tempfile.mkdtemp()
    try:
        temp_db_path = os.path.join(temp_dir, "test_edit.db")
        
        # Create and initialize database
        db = DatabaseManager(temp_db_path)
        db.crear_tablas_nucleo()
        db.sembrar_datos_iniciales()
        db.asegurar_tabla_alquiler_meta()
        db.asegurar_tabla_equipos_entidades()
        
        # Create a proyecto
        db.execute("INSERT INTO proyectos (nombre, moneda) VALUES (?, ?)", ("Proyecto Test", "RD$"))
        proyecto_id = 1
        
        # Create cliente, operador, equipo
        db.execute(
            "INSERT INTO equipos_entidades (proyecto_id, nombre, tipo) VALUES (?, ?, ?)",
            (proyecto_id, "Cliente Test", "Cliente")
        )
        cliente_id = db.fetchone("SELECT id FROM equipos_entidades WHERE nombre = ?", ("Cliente Test",))['id']
        
        db.execute(
            "INSERT INTO equipos_entidades (proyecto_id, nombre, tipo) VALUES (?, ?, ?)",
            (proyecto_id, "Operador Test", "Operador")
        )
        operador_id = db.fetchone("SELECT id FROM equipos_entidades WHERE nombre = ?", ("Operador Test",))['id']
        
        db.execute(
            "INSERT INTO equipos (proyecto_id, nombre, marca, modelo, categoria, equipo, activo) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (proyecto_id, "Excavadora", "CAT", "320", "Pesados", "Excavadora", 1)
        )
        equipo_id = db.fetchone("SELECT id FROM equipos WHERE nombre = ?", ("Excavadora",))['id']
        
        # Create a category and account
        db.execute("INSERT INTO categorias (nombre) VALUES (?)", ("ALQUILERES",))
        categoria_id = db.fetchone("SELECT id FROM categorias WHERE nombre = ?", ("ALQUILERES",))['id']
        
        db.execute("INSERT INTO cuentas (nombre, tipo_cuenta) VALUES (?, ?)", ("Cuenta Principal", "Principal"))
        cuenta_id = db.fetchone("SELECT id FROM cuentas WHERE nombre = ?", ("Cuenta Principal",))['id']
        
        # Create initial alquiler
        transaccion_id = uuid.uuid4().hex
        initial_horas = 8.0
        initial_precio = 1000.0
        initial_monto = initial_horas * initial_precio
        
        db.execute("""
            INSERT INTO transacciones
            (id, proyecto_id, cuenta_id, categoria_id, tipo, descripcion, monto, fecha,
             cliente_id, operador_id, equipo_id, horas, precio_por_hora, conduce, ubicacion, pagado)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            transaccion_id, proyecto_id, cuenta_id, categoria_id, 'Ingreso',
            "Alquiler inicial", initial_monto, "2025-01-10",
            cliente_id, operador_id, equipo_id, initial_horas, initial_precio,
            "COND-001", "Ubicación Original", 0
        ))
        
        db.execute("""
            INSERT INTO equipos_alquiler_meta
            (transaccion_id, proyecto_id, cliente_id, operador_id, horas, precio_por_hora,
             conduce, ubicacion, equipo_id)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            transaccion_id, proyecto_id, cliente_id, operador_id,
            initial_horas, initial_precio, "COND-001", "Ubicación Original", equipo_id
        ))
        
        # Verify initial state
        trans_before = db.fetchone("SELECT * FROM transacciones WHERE id = ?", (transaccion_id,))
        meta_before = db.fetchone("SELECT * FROM equipos_alquiler_meta WHERE transaccion_id = ?", (transaccion_id,))
        
        assert trans_before['horas'] == initial_horas, "Initial transaccion horas should match"
        assert meta_before['horas'] == initial_horas, "Initial meta horas should match"
        assert trans_before['ubicacion'] == "Ubicación Original", "Initial ubicacion should match"
        assert meta_before['ubicacion'] == "Ubicación Original", "Initial meta ubicacion should match"
        
        print(f"  ✓ Initial alquiler created: {initial_horas} horas, {initial_precio} precio")
        
        # Update alquiler (simulating edit)
        new_horas = 12.0
        new_precio = 1200.0
        new_monto = new_horas * new_precio
        new_ubicacion = "Nueva Ubicación"
        new_conduce = "COND-002"
        
        datos_actualizacion = {
            'horas': new_horas,
            'precio_por_hora': new_precio,
            'monto': new_monto,
            'ubicacion': new_ubicacion,
            'conduce': new_conduce,
            'fecha': "2025-01-11"
        }
        
        success = db.actualizar_alquiler(transaccion_id, datos_actualizacion)
        assert success, "actualizar_alquiler should return True"
        
        # Verify updates in both tables
        trans_after = db.fetchone("SELECT * FROM transacciones WHERE id = ?", (transaccion_id,))
        meta_after = db.fetchone("SELECT * FROM equipos_alquiler_meta WHERE transaccion_id = ?", (transaccion_id,))
        
        # Check transacciones table
        assert trans_after['horas'] == new_horas, f"Transaccion horas should be {new_horas}, got {trans_after['horas']}"
        assert trans_after['precio_por_hora'] == new_precio, f"Transaccion precio should be {new_precio}"
        assert trans_after['monto'] == new_monto, f"Transaccion monto should be {new_monto}"
        assert trans_after['ubicacion'] == new_ubicacion, f"Transaccion ubicacion should be '{new_ubicacion}'"
        assert trans_after['conduce'] == new_conduce, f"Transaccion conduce should be '{new_conduce}'"
        
        # Check equipos_alquiler_meta table
        assert meta_after['horas'] == new_horas, f"Meta horas should be {new_horas}, got {meta_after['horas']}"
        assert meta_after['precio_por_hora'] == new_precio, f"Meta precio should be {new_precio}"
        assert meta_after['ubicacion'] == new_ubicacion, f"Meta ubicacion should be '{new_ubicacion}'"
        assert meta_after['conduce'] == new_conduce, f"Meta conduce should be '{new_conduce}'"
        
        # Verify no duplication occurred
        trans_count = db.fetchone("SELECT COUNT(*) as cnt FROM transacciones WHERE id = ?", (transaccion_id,))
        assert trans_count['cnt'] == 1, "Should have exactly 1 transaction record (no duplication)"
        
        meta_count = db.fetchone("SELECT COUNT(*) as cnt FROM equipos_alquiler_meta WHERE transaccion_id = ?", (transaccion_id,))
        assert meta_count['cnt'] == 1, "Should have exactly 1 meta record (no duplication)"
        
        print(f"  ✓ Alquiler updated successfully: {new_horas} horas, {new_precio} precio")
        print(f"  ✓ Both transacciones and equipos_alquiler_meta updated")
        print(f"  ✓ No duplication detected")
        
        print("✓ Test passed!")
        return True
        
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


if __name__ == "__main__":
    print("=" * 60)
    print("Testing Alquiler Edit Fix")
    print("=" * 60)
    
    try:
        test_actualizar_alquiler_updates_both_tables()
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
