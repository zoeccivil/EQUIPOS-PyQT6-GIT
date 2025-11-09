"""
Base repository interface for EQUIPOS PyQt6.
Defines the contract that all repository implementations must follow.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class BaseRepository(ABC):
    """Abstract base class for repository pattern implementation."""

    # --- PROYECTO METHODS ---
    @abstractmethod
    def obtener_proyectos(self) -> List[Dict[str, Any]]:
        """Get all projects."""
        pass

    @abstractmethod
    def obtener_proyecto_por_id(self, proyecto_id: int) -> Optional[Dict[str, Any]]:
        """Get project by ID."""
        pass

    # --- EQUIPO METHODS ---
    @abstractmethod
    def obtener_equipos(self, proyecto_id: int) -> List[Dict[str, Any]]:
        """Get all equipment for a project."""
        pass

    @abstractmethod
    def obtener_equipo_por_id(self, equipo_id: int) -> Optional[Dict[str, Any]]:
        """Get equipment by ID."""
        pass

    @abstractmethod
    def guardar_equipo(self, datos: Dict[str, Any], equipo_id: Optional[int] = None) -> bool:
        """Save or update equipment."""
        pass

    @abstractmethod
    def eliminar_equipo(self, equipo_id: int) -> bool:
        """Delete equipment."""
        pass

    # --- TRANSACCION METHODS ---
    @abstractmethod
    def obtener_transaccion_por_id(self, transaccion_id: str) -> Optional[Dict[str, Any]]:
        """Get transaction by ID."""
        pass

    @abstractmethod
    def obtener_transacciones_por_proyecto(self, proyecto_id: int, filtros: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get transactions for a project with optional filters."""
        pass

    @abstractmethod
    def crear_nuevo_alquiler(self, datos: Dict[str, Any]) -> str:
        """Create new rental transaction."""
        pass

    @abstractmethod
    def actualizar_alquiler(self, transaccion_id: str, datos: Dict[str, Any]) -> bool:
        """Update existing rental transaction."""
        pass

    @abstractmethod
    def eliminar_alquiler(self, alquiler_id: str) -> bool:
        """Delete rental transaction."""
        pass

    # --- ENTIDAD METHODS (Clientes, Operadores) ---
    @abstractmethod
    def obtener_entidades_por_tipo(self, proyecto_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get entities (clients/operators) by type."""
        pass

    @abstractmethod
    def obtener_entidades_equipo_por_tipo(self, proyecto_id: int, tipo_entidad: str) -> List[Dict[str, Any]]:
        """Get equipment entities by type (Cliente/Operador)."""
        pass

    @abstractmethod
    def obtener_clientes_por_proyecto(self, proyecto_id: int) -> List[Dict[str, Any]]:
        """Get all clients for a project."""
        pass

    @abstractmethod
    def obtener_operadores_por_proyecto(self, proyecto_id: int) -> List[Dict[str, Any]]:
        """Get all operators for a project."""
        pass

    # --- MANTENIMIENTO METHODS ---
    @abstractmethod
    def registrar_mantenimiento(self, datos: Dict[str, Any]) -> int:
        """Register new maintenance record."""
        pass

    @abstractmethod
    def actualizar_mantenimiento(self, datos: Dict[str, Any]) -> int:
        """Update maintenance record."""
        pass

    @abstractmethod
    def eliminar_mantenimiento(self, mantenimiento_id: int) -> bool:
        """Delete maintenance record."""
        pass

    @abstractmethod
    def obtener_mantenimiento_por_id(self, mantenimiento_id: int) -> Optional[Dict[str, Any]]:
        """Get maintenance record by ID."""
        pass

    @abstractmethod
    def obtener_mantenimientos_por_equipo(self, equipo_id: int, limite: int = 200) -> List[Dict[str, Any]]:
        """Get maintenance records for equipment."""
        pass

    # --- ABONO/PAGO METHODS ---
    @abstractmethod
    def registrar_abono_general_cliente(self, datos_pago: Dict[str, Any]) -> int:
        """Register client payment."""
        pass

    @abstractmethod
    def actualizar_abono(self, pago_id: int, nueva_fecha: str, nuevo_monto: float, nuevo_comentario: str) -> bool:
        """Update payment record."""
        pass

    @abstractmethod
    def eliminar_abono(self, pago_ids: List[int]) -> bool:
        """Delete payment records."""
        pass

    @abstractmethod
    def obtener_abono_por_id(self, pago_id: int) -> Optional[Dict[str, Any]]:
        """Get payment by ID."""
        pass

    @abstractmethod
    def obtener_lista_abonos(self, proyecto_id: int, filtros: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get list of payments with filters."""
        pass

    # --- DASHBOARD & KPI METHODS ---
    @abstractmethod
    def obtener_kpis_dashboard(self, proyecto_id: int, anio: int, mes: int, equipo_id: Optional[int] = None) -> Dict[str, Any]:
        """Get KPIs for dashboard."""
        pass

    # --- UTILITY METHODS ---
    @abstractmethod
    def crear_tablas_nucleo(self) -> None:
        """Create core database tables."""
        pass

    @abstractmethod
    def asegurar_tabla_pagos(self) -> None:
        """Ensure payments table exists."""
        pass

    @abstractmethod
    def asegurar_tabla_mantenimientos(self) -> None:
        """Ensure maintenance table exists."""
        pass

    @abstractmethod
    def asegurar_tabla_alquiler_meta(self) -> None:
        """Ensure rental metadata table exists."""
        pass
