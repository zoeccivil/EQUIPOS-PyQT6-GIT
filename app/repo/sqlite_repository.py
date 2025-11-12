"""
SQLite Repository Implementation

Wraps the existing DatabaseManager (logic.py) to implement the AbstractRepository interface.
This allows the existing SQLite functionality to work through the new repository pattern.
"""
from typing import List, Dict, Optional, Any
import sys
import os

# Add parent directory to path to import logic module
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from logic import DatabaseManager
from app.repo.abstract_repository import AbstractRepository


class SQLiteRepository(AbstractRepository):
    """
    SQLite implementation of AbstractRepository.
    
    This class wraps the existing DatabaseManager to provide a consistent
    interface for data access operations.
    """
    
    def __init__(self, db_manager: DatabaseManager):
        """
        Initialize with an existing DatabaseManager instance.
        
        Args:
            db_manager: The DatabaseManager instance from logic.py
        """
        self.db = db_manager
    
    # ==================== PROJECT OPERATIONS ====================
    
    def obtener_proyectos(self) -> List[Dict[str, Any]]:
        """Get all projects."""
        return self.db.obtener_proyectos()
    
    def obtener_proyecto_por_id(self, proyecto_id: int) -> Optional[Dict[str, Any]]:
        """Get a project by ID."""
        return self.db.obtener_proyecto_por_id(proyecto_id)
    
    # ==================== EQUIPMENT OPERATIONS ====================
    
    def obtener_equipos(self, proyecto_id: int) -> List[Dict[str, Any]]:
        """Get all equipment for a project."""
        return self.db.obtener_equipos(proyecto_id)
    
    def obtener_equipo_por_id(self, equipo_id: int) -> Optional[Dict[str, Any]]:
        """Get equipment by ID."""
        return self.db.obtener_equipo_por_id(equipo_id)
    
    def obtener_todos_los_equipos(self) -> List[Dict[str, Any]]:
        """Get all equipment across all projects."""
        return self.db.obtener_todos_los_equipos()
    
    def guardar_equipo(self, datos: Dict[str, Any], equipo_id: Optional[int] = None) -> bool:
        """Save (create or update) equipment."""
        return self.db.guardar_equipo(datos, equipo_id)
    
    def eliminar_equipo(self, equipo_id: int) -> bool:
        """Delete equipment by ID."""
        return self.db.eliminar_equipo(equipo_id)
    
    # ==================== ENTITY OPERATIONS (Clients, Operators) ====================
    
    def obtener_entidades_por_tipo(self, proyecto_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get entities (generic, from equipos table for backward compatibility)."""
        return self.db.obtener_entidades_por_tipo(proyecto_id)
    
    def obtener_entidades_equipo_por_tipo(self, proyecto_id: int, tipo_entidad: str) -> List[Dict[str, Any]]:
        """Get entities by type (Cliente, Operador) from equipos_entidades table."""
        return self.db.obtener_entidades_equipo_por_tipo(proyecto_id, tipo_entidad)
    
    def guardar_entidad(self, datos: Dict[str, Any], entidad_id: Optional[int] = None) -> bool:
        """Save (create or update) an entity."""
        return self.db.guardar_entidad(datos, entidad_id)
    
    def eliminar_entidad(self, entidad_id: int) -> bool:
        """Delete an entity by ID."""
        return self.db.eliminar_entidad(entidad_id)
    
    def obtener_entidad_por_id(self, entidad_id: int) -> Optional[Dict[str, Any]]:
        """Get an entity by ID."""
        return self.db.obtener_entidad_por_id(entidad_id)
    
    # ==================== RENTAL/TRANSACTION OPERATIONS ====================
    
    def obtener_transacciones_por_proyecto(self, proyecto_id: int, filtros: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get transactions for a project with optional filters."""
        return self.db.obtener_transacciones_por_proyecto(proyecto_id, filtros)
    
    def obtener_transaccion_por_id(self, transaccion_id: str) -> Optional[Dict[str, Any]]:
        """Get a transaction by ID."""
        return self.db.obtener_transaccion_por_id(transaccion_id)
    
    def obtener_detalles_alquiler(self, transaccion_id: str) -> Optional[Dict[str, Any]]:
        """Get rental details including related entity names."""
        return self.db.obtener_detalles_alquiler(transaccion_id)
    
    def crear_nuevo_alquiler(self, datos: Dict[str, Any]) -> Optional[str]:
        """Create a new rental. Returns the transaction ID."""
        return self.db.crear_nuevo_alquiler(datos)
    
    def actualizar_alquiler(self, transaccion_id: str, datos: Dict[str, Any]) -> bool:
        """Update an existing rental."""
        return self.db.actualizar_alquiler(transaccion_id, datos)
    
    def eliminar_alquiler(self, alquiler_id: str) -> bool:
        """Delete a rental by ID."""
        return self.db.eliminar_alquiler(alquiler_id)
    
    # ==================== MAINTENANCE OPERATIONS ====================
    
    def obtener_mantenimientos_por_equipo(self, equipo_id: int, limite: int = 200) -> List[Dict[str, Any]]:
        """Get maintenance records for equipment."""
        return self.db.obtener_mantenimientos_por_equipo(equipo_id, limite)
    
    def obtener_mantenimiento_por_id(self, mantenimiento_id: int) -> Optional[Dict[str, Any]]:
        """Get a maintenance record by ID."""
        return self.db.obtener_mantenimiento_por_id(mantenimiento_id)
    
    def registrar_mantenimiento(self, datos: Dict[str, Any]) -> int:
        """Register a new maintenance record. Returns the new ID."""
        return self.db.registrar_mantenimiento(datos)
    
    def actualizar_mantenimiento(self, datos: Dict[str, Any]) -> bool:
        """Update a maintenance record."""
        return self.db.actualizar_mantenimiento(datos)
    
    def eliminar_mantenimiento(self, mantenimiento_id: int) -> bool:
        """Delete a maintenance record by ID."""
        return self.db.eliminar_mantenimiento(mantenimiento_id)
    
    # ==================== PAYMENT/ABONO OPERATIONS ====================
    
    def obtener_lista_abonos(self, proyecto_id: int, filtros: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get list of payments/abonos with filters."""
        return self.db.obtener_lista_abonos(proyecto_id, filtros)
    
    def obtener_abono_por_id(self, pago_id: int) -> Optional[Dict[str, Any]]:
        """Get a payment/abono by ID."""
        return self.db.obtener_abono_por_id(pago_id)
    
    def registrar_abono_general_cliente(self, datos_pago: Dict[str, Any]) -> int:
        """Register a client payment. Returns the new payment ID."""
        return self.db.registrar_abono_general_cliente(datos_pago)
    
    def actualizar_abono(self, pago_id: int, nueva_fecha: str, nuevo_monto: float, nuevo_comentario: str) -> bool:
        """Update a payment/abono."""
        return self.db.actualizar_abono(pago_id, nueva_fecha, nuevo_monto, nuevo_comentario)
    
    def eliminar_abono(self, pago_ids: List[int]) -> bool:
        """Delete payments/abonos by IDs."""
        return self.db.eliminar_abono(pago_ids)
    
    # ==================== DASHBOARD/KPI OPERATIONS ====================
    
    def obtener_kpis_dashboard(self, proyecto_id: int, anio: int, mes: int, equipo_id: Optional[int] = None) -> Dict[str, Any]:
        """Get KPIs for dashboard."""
        return self.db.obtener_kpis_dashboard(proyecto_id, anio, mes, equipo_id)
    
    def obtener_fecha_primera_transaccion(self, proyecto_id: int) -> Optional[str]:
        """Get the date of the first transaction for a project."""
        return self.db.obtener_fecha_primera_transaccion(proyecto_id)
    
    # ==================== ACCOUNT/CATEGORY OPERATIONS ====================
    
    def listar_cuentas(self) -> List[Dict[str, Any]]:
        """List all accounts."""
        return self.db.listar_cuentas()
    
    def obtener_cuentas_por_proyecto(self, proyecto_id: int) -> List[Dict[str, Any]]:
        """Get accounts for a project."""
        return self.db.obtener_cuentas_por_proyecto(proyecto_id)
    
    def obtener_categorias_por_proyecto(self, proyecto_id: int, tipo: str = "Gasto") -> List[Dict[str, Any]]:
        """Get categories for a project by type."""
        return self.db.obtener_categorias_por_proyecto(proyecto_id, tipo)
    
    # ==================== TABLE MANAGEMENT ====================
    
    def asegurar_tabla_equipos_entidades(self) -> None:
        """Ensure the equipos_entidades table exists."""
        self.db.asegurar_tabla_equipos_entidades()
    
    def asegurar_tabla_pagos(self) -> None:
        """Ensure the pagos table exists."""
        self.db.asegurar_tabla_pagos()
    
    def asegurar_tabla_mantenimientos(self) -> None:
        """Ensure the mantenimientos table exists."""
        self.db.asegurar_tabla_mantenimientos()
    
    # ==================== DIRECT DATABASE ACCESS ====================
    # For cases where the existing code needs direct access to the underlying DatabaseManager
    
    def get_db_manager(self) -> DatabaseManager:
        """
        Get the underlying DatabaseManager instance.
        
        This is provided for backward compatibility with existing code that needs
        direct access to DatabaseManager methods not yet abstracted in the repository.
        """
        return self.db
