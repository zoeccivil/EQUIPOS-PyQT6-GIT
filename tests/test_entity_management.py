"""
Test for entity management with telefono and cedula fields.
Verifies that entities (Clientes/Operadores) can be created and retrieved with contact information.
"""

import sys
import os
import unittest
import tempfile

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from logic import DatabaseManager


class TestEntityManagement(unittest.TestCase):
    """Test cases for entity management with telefono and cedula."""

    def setUp(self):
        """Create a temporary database for testing."""
        self.temp_db = tempfile.NamedTemporaryFile(mode='w', suffix='.db', delete=False)
        self.temp_db.close()
        self.db_path = self.temp_db.name
        self.db = DatabaseManager(self.db_path)
        
        # Create core tables
        self.db.crear_tablas_nucleo()
        self.db.asegurar_tabla_equipos_entidades()
        
        # Create test project
        self.db.execute("INSERT INTO proyectos (id, nombre) VALUES (?, ?)", (1, "Test Project"))

    def tearDown(self):
        """Clean up temporary database."""
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)

    def test_create_entity_with_telefono_cedula(self):
        """Test creating an entity with telefono and cedula."""
        datos = {
            "proyecto_id": 1,
            "tipo": "Cliente",
            "nombre": "Juan Pérez",
            "telefono": "809-555-1234",
            "cedula": "001-1234567-8",
            "activo": 1
        }
        
        # Create entity
        result = self.db.guardar_entidad(datos)
        self.assertTrue(result, "Failed to create entity")
        
        # Retrieve entities
        entidades = self.db.obtener_entidades_equipo_por_tipo(1, "Cliente")
        self.assertEqual(len(entidades), 1, "Should have 1 entity")
        
        # Verify fields
        entidad = entidades[0]
        self.assertEqual(entidad['nombre'], "Juan Pérez")
        self.assertEqual(entidad['telefono'], "809-555-1234")
        self.assertEqual(entidad['cedula'], "001-1234567-8")
        self.assertEqual(entidad['activo'], 1)

    def test_create_entity_without_telefono_cedula(self):
        """Test creating an entity without telefono and cedula (optional fields)."""
        datos = {
            "proyecto_id": 1,
            "tipo": "Operador",
            "nombre": "María García",
            "telefono": None,
            "cedula": None,
            "activo": 1
        }
        
        # Create entity
        result = self.db.guardar_entidad(datos)
        self.assertTrue(result, "Failed to create entity without telefono/cedula")
        
        # Retrieve entities
        entidades = self.db.obtener_entidades_equipo_por_tipo(1, "Operador")
        self.assertEqual(len(entidades), 1, "Should have 1 entity")
        
        # Verify fields
        entidad = entidades[0]
        self.assertEqual(entidad['nombre'], "María García")
        # telefono and cedula should be None or empty
        self.assertIn(entidad.get('telefono'), [None, ''])
        self.assertIn(entidad.get('cedula'), [None, ''])

    def test_update_entity_with_telefono_cedula(self):
        """Test updating an entity to add telefono and cedula."""
        # Create entity without contact info
        datos = {
            "proyecto_id": 1,
            "tipo": "Cliente",
            "nombre": "Pedro López",
            "telefono": None,
            "cedula": None,
            "activo": 1
        }
        self.db.guardar_entidad(datos)
        
        # Get entity ID
        entidades = self.db.obtener_entidades_equipo_por_tipo(1, "Cliente")
        entidad_id = entidades[0]['id']
        
        # Update with contact info
        datos_actualizados = {
            "proyecto_id": 1,
            "tipo": "Cliente",
            "nombre": "Pedro López",
            "telefono": "829-555-9876",
            "cedula": "001-9876543-2",
            "activo": 1
        }
        
        result = self.db.guardar_entidad(datos_actualizados, entidad_id)
        self.assertTrue(result, "Failed to update entity")
        
        # Verify update
        entidad = self.db.obtener_entidad_por_id(entidad_id)
        self.assertEqual(entidad['telefono'], "829-555-9876")
        self.assertEqual(entidad['cedula'], "001-9876543-2")

    def test_obtener_entidad_por_id(self):
        """Test retrieving entity by ID."""
        # Create entity
        datos = {
            "proyecto_id": 1,
            "tipo": "Cliente",
            "nombre": "Ana Martínez",
            "telefono": "849-555-5555",
            "cedula": "001-5555555-5",
            "activo": 1
        }
        self.db.guardar_entidad(datos)
        
        # Get entity by type to find ID
        entidades = self.db.obtener_entidades_equipo_por_tipo(1, "Cliente")
        entidad_id = entidades[0]['id']
        
        # Get entity by ID
        entidad = self.db.obtener_entidad_por_id(entidad_id)
        self.assertIsNotNone(entidad)
        self.assertEqual(entidad['nombre'], "Ana Martínez")
        self.assertEqual(entidad['telefono'], "849-555-5555")
        self.assertEqual(entidad['cedula'], "001-5555555-5")

    def test_eliminar_entidad(self):
        """Test deleting (marking inactive) an entity."""
        # Create entity
        datos = {
            "proyecto_id": 1,
            "tipo": "Operador",
            "nombre": "Carlos Rodríguez",
            "telefono": "809-123-4567",
            "cedula": "001-1111111-1",
            "activo": 1
        }
        self.db.guardar_entidad(datos)
        
        # Get entity ID
        entidades = self.db.obtener_entidades_equipo_por_tipo(1, "Operador")
        entidad_id = entidades[0]['id']
        
        # Delete entity
        result = self.db.eliminar_entidad(entidad_id)
        self.assertTrue(result, "Failed to delete entity")
        
        # Verify entity is marked inactive
        entidad = self.db.obtener_entidad_por_id(entidad_id)
        self.assertEqual(entidad['activo'], 0, "Entity should be inactive")

    def test_table_migration_adds_columns(self):
        """Test that asegurar_tabla_equipos_entidades adds telefono and cedula columns."""
        # The setUp already calls asegurar_tabla_equipos_entidades
        # Let's verify the columns exist by trying to insert data
        
        datos = {
            "proyecto_id": 1,
            "tipo": "Cliente",
            "nombre": "Test Migration",
            "telefono": "123-456-7890",
            "cedula": "ABC-123",
            "activo": 1
        }
        
        # This should work without error if columns exist
        try:
            result = self.db.guardar_entidad(datos)
            self.assertTrue(result, "Migration should add telefono/cedula columns")
        except Exception as e:
            self.fail(f"Migration failed to add columns: {e}")


if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)
