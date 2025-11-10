"""
Abstract Repository Interface

Defines the contract for all repository implementations (SQLite, Firestore, etc.).
This allows the application to work with different persistence backends without
changing the business logic.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Any


class AbstractRepository(ABC):
    """
    Abstract base class for all repository implementations.
    
    All repositories must implement these methods to ensure consistent
    behavior across different persistence backends (SQLite, Firestore, etc.)
    """
    
    # ==================== PROJECT OPERATIONS ====================
    
    @abstractmethod
    def obtener_proyectos(self) -> List[Dict[str, Any]]:
        """Get all projects."""
        pass
    
    @abstractmethod
    def obtener_proyecto_por_id(self, proyecto_id: int) -> Optional[Dict[str, Any]]:
        """Get a project by ID."""
        pass
    
    # ==================== EQUIPMENT OPERATIONS ====================
    
    @abstractmethod
    def obtener_equipos(self, proyecto_id: int) -> List[Dict[str, Any]]:
        """Get all equipment for a project."""
        pass
    
    @abstractmethod
    def obtener_equipo_por_id(self, equipo_id: int) -> Optional[Dict[str, Any]]:
        """Get equipment by ID."""
        pass
    
    @abstractmethod
    def obtener_todos_los_equipos(self) -> List[Dict[str, Any]]:
        """Get all equipment across all projects."""
        pass
    
    @abstractmethod
    def guardar_equipo(self, datos: Dict[str, Any], equipo_id: Optional[int] = None) -> bool:
        """Save (create or update) equipment."""
        pass
    
    @abstractmethod
    def eliminar_equipo(self, equipo_id: int) -> bool:
        """Delete equipment by ID."""
        pass
    
    # ==================== ENTITY OPERATIONS (Clients, Operators) ====================
    
    @abstractmethod
    def obtener_entidades_por_tipo(self, proyecto_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get entities (generic, from equipos table for backward compatibility)."""
        pass
    
    @abstractmethod
    def obtener_entidades_equipo_por_tipo(self, proyecto_id: int, tipo_entidad: str) -> List[Dict[str, Any]]:
        """Get entities by type (Cliente, Operador) from equipos_entidades table."""
        pass
    
    @abstractmethod
    def guardar_entidad(self, datos: Dict[str, Any], entidad_id: Optional[int] = None) -> bool:
        """Save (create or update) an entity."""
        pass
    
    @abstractmethod
    def eliminar_entidad(self, entidad_id: int) -> bool:
        """Delete an entity by ID."""
        pass
    
    @abstractmethod
    def obtener_entidad_por_id(self, entidad_id: int) -> Optional[Dict[str, Any]]:
        """Get an entity by ID."""
        pass
    
    # ==================== RENTAL/TRANSACTION OPERATIONS ====================
    
    @abstractmethod
    def obtener_transacciones_por_proyecto(self, proyecto_id: int, filtros: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get transactions for a project with optional filters."""
        pass
    
    @abstractmethod
    def obtener_transaccion_por_id(self, transaccion_id: str) -> Optional[Dict[str, Any]]:
        """Get a transaction by ID."""
        pass
    
    @abstractmethod
    def obtener_detalles_alquiler(self, transaccion_id: str) -> Optional[Dict[str, Any]]:
        """Get rental details including related entity names."""
        pass
    
    @abstractmethod
    def crear_nuevo_alquiler(self, datos: Dict[str, Any]) -> Optional[str]:
        """Create a new rental. Returns the transaction ID."""
        pass
    
    @abstractmethod
    def actualizar_alquiler(self, transaccion_id: str, datos: Dict[str, Any]) -> bool:
        """Update an existing rental."""
        pass
    
    @abstractmethod
    def eliminar_alquiler(self, alquiler_id: str) -> bool:
        """Delete a rental by ID."""
        pass
    
    # ==================== MAINTENANCE OPERATIONS ====================
    
    @abstractmethod
    def obtener_mantenimientos_por_equipo(self, equipo_id: int, limite: int = 200) -> List[Dict[str, Any]]:
        """Get maintenance records for equipment."""
        pass
    
    @abstractmethod
    def obtener_mantenimiento_por_id(self, mantenimiento_id: int) -> Optional[Dict[str, Any]]:
        """Get a maintenance record by ID."""
        pass
    
    @abstractmethod
    def registrar_mantenimiento(self, datos: Dict[str, Any]) -> int:
        """Register a new maintenance record. Returns the new ID."""
        pass
    
    @abstractmethod
    def actualizar_mantenimiento(self, datos: Dict[str, Any]) -> bool:
        """Update a maintenance record."""
        pass
    
    @abstractmethod
    def eliminar_mantenimiento(self, mantenimiento_id: int) -> bool:
        """Delete a maintenance record by ID."""
        pass
    
    # ==================== PAYMENT/ABONO OPERATIONS ====================
    
    @abstractmethod
    def obtener_lista_abonos(self, proyecto_id: int, filtros: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get list of payments/abonos with filters."""
        pass
    
    @abstractmethod
    def obtener_abono_por_id(self, pago_id: int) -> Optional[Dict[str, Any]]:
        """Get a payment/abono by ID."""
        pass
    
    @abstractmethod
    def registrar_abono_general_cliente(self, datos_pago: Dict[str, Any]) -> int:
        """Register a client payment. Returns the new payment ID."""
        pass
    
    @abstractmethod
    def actualizar_abono(self, pago_id: int, nueva_fecha: str, nuevo_monto: float, nuevo_comentario: str) -> bool:
        """Update a payment/abono."""
        pass
    
    @abstractmethod
    def eliminar_abono(self, pago_ids: List[int]) -> bool:
        """Delete payments/abonos by IDs."""
        pass
    
    # ==================== DASHBOARD/KPI OPERATIONS ====================
    
    @abstractmethod
    def obtener_kpis_dashboard(self, proyecto_id: int, anio: int, mes: int, equipo_id: Optional[int] = None) -> Dict[str, Any]:
        """Get KPIs for dashboard."""
        pass
    
    @abstractmethod
    def obtener_fecha_primera_transaccion(self, proyecto_id: int) -> Optional[str]:
        """Get the date of the first transaction for a project."""
        pass
    
    # ==================== ACCOUNT/CATEGORY OPERATIONS ====================
    
    @abstractmethod
    def listar_cuentas(self) -> List[Dict[str, Any]]:
        """List all accounts."""
        pass
    
    @abstractmethod
    def obtener_cuentas_por_proyecto(self, proyecto_id: int) -> List[Dict[str, Any]]:
        """Get accounts for a project."""
        pass
    
    @abstractmethod
    def obtener_categorias_por_proyecto(self, proyecto_id: int, tipo: str = "Gasto") -> List[Dict[str, Any]]:
        """Get categories for a project by type."""
        pass
    
    # ==================== TABLE MANAGEMENT ====================
    
    @abstractmethod
    def asegurar_tabla_equipos_entidades(self) -> None:
        """Ensure the equipos_entidades table exists."""
        pass
    
    @abstractmethod
    def asegurar_tabla_pagos(self) -> None:
        """Ensure the pagos table exists."""
        pass
    
    @abstractmethod
    def asegurar_tabla_mantenimientos(self) -> None:
        """Ensure the mantenimientos table exists."""
        pass
