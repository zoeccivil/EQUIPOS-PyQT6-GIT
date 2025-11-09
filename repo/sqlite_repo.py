"""
SQLite repository implementation for EQUIPOS PyQt6.
Wraps the existing DatabaseManager from logic.py to provide repository interface.
"""

import logging
from typing import List, Dict, Any, Optional
from .base_repo import BaseRepository
from logic import DatabaseManager

logger = logging.getLogger(__name__)


class SQLiteRepository(BaseRepository):
    """SQLite implementation of the repository pattern."""

    def __init__(self, db_path: str = "progain_database.db"):
        """Initialize SQLite repository with database path."""
        self.db = DatabaseManager(db_path)
        logger.info(f"SQLiteRepository initialized with db_path: {db_path}")

    # --- PROYECTO METHODS ---
    def obtener_proyectos(self) -> List[Dict[str, Any]]:
        """Get all projects."""
        return self.db.obtener_proyectos()

    def obtener_proyecto_por_id(self, proyecto_id: int) -> Optional[Dict[str, Any]]:
        """Get project by ID."""
        return self.db.obtener_proyecto_por_id(proyecto_id)

    # --- EQUIPO METHODS ---
    def obtener_equipos(self, proyecto_id: int) -> List[Dict[str, Any]]:
        """Get all equipment for a project."""
        return self.db.obtener_equipos(proyecto_id)

    def obtener_equipo_por_id(self, equipo_id: int) -> Optional[Dict[str, Any]]:
        """Get equipment by ID."""
        return self.db.obtener_equipo_por_id(equipo_id)

    def guardar_equipo(self, datos: Dict[str, Any], equipo_id: Optional[int] = None) -> bool:
        """Save or update equipment."""
        return self.db.guardar_equipo(datos, equipo_id)

    def eliminar_equipo(self, equipo_id: int) -> bool:
        """Delete equipment."""
        return self.db.eliminar_equipo(equipo_id)

    # --- TRANSACCION METHODS ---
    def obtener_transaccion_por_id(self, transaccion_id: str) -> Optional[Dict[str, Any]]:
        """Get transaction by ID."""
        return self.db.obtener_transaccion_por_id(transaccion_id)

    def obtener_transacciones_por_proyecto(self, proyecto_id: int, filtros: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Get transactions for a project with optional filters."""
        return self.db.obtener_transacciones_por_proyecto(proyecto_id, filtros)

    def crear_nuevo_alquiler(self, datos: Dict[str, Any]) -> str:
        """Create new rental transaction."""
        return self.db.crear_nuevo_alquiler(datos)

    def actualizar_alquiler(self, transaccion_id: str, datos: Dict[str, Any]) -> bool:
        """Update existing rental transaction."""
        return self.db.actualizar_alquiler(transaccion_id, datos)

    def eliminar_alquiler(self, alquiler_id: str) -> bool:
        """Delete rental transaction."""
        return self.db.eliminar_alquiler(alquiler_id)

    # --- ENTIDAD METHODS (Clientes, Operadores) ---
    def obtener_entidades_por_tipo(self, proyecto_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get entities (clients/operators) by type."""
        return self.db.obtener_entidades_por_tipo(proyecto_id)

    def obtener_entidades_equipo_por_tipo(self, proyecto_id: int, tipo_entidad: str) -> List[Dict[str, Any]]:
        """Get equipment entities by type (Cliente/Operador)."""
        return self.db.obtener_entidades_equipo_por_tipo(proyecto_id, tipo_entidad)

    def obtener_clientes_por_proyecto(self, proyecto_id: int) -> List[Dict[str, Any]]:
        """Get all clients for a project."""
        return self.db.obtener_clientes_por_proyecto(proyecto_id)

    def obtener_operadores_por_proyecto(self, proyecto_id: int) -> List[Dict[str, Any]]:
        """Get all operators for a project."""
        return self.db.obtener_operadores_por_proyecto(proyecto_id)

    # --- MANTENIMIENTO METHODS ---
    def registrar_mantenimiento(self, datos: Dict[str, Any]) -> int:
        """Register new maintenance record."""
        return self.db.registrar_mantenimiento(datos)

    def actualizar_mantenimiento(self, datos: Dict[str, Any]) -> int:
        """Update maintenance record."""
        return self.db.actualizar_mantenimiento(datos)

    def eliminar_mantenimiento(self, mantenimiento_id: int) -> bool:
        """Delete maintenance record."""
        return self.db.eliminar_mantenimiento(mantenimiento_id)

    def obtener_mantenimiento_por_id(self, mantenimiento_id: int) -> Optional[Dict[str, Any]]:
        """Get maintenance record by ID."""
        return self.db.obtener_mantenimiento_por_id(mantenimiento_id)

    def obtener_mantenimientos_por_equipo(self, equipo_id: int, limite: int = 200) -> List[Dict[str, Any]]:
        """Get maintenance records for equipment."""
        return self.db.obtener_mantenimientos_por_equipo(equipo_id, limite)

    # --- ABONO/PAGO METHODS ---
    def registrar_abono_general_cliente(self, datos_pago: Dict[str, Any]) -> int:
        """Register client payment."""
        return self.db.registrar_abono_general_cliente(datos_pago)

    def actualizar_abono(self, pago_id: int, nueva_fecha: str, nuevo_monto: float, nuevo_comentario: str) -> bool:
        """Update payment record."""
        return self.db.actualizar_abono(pago_id, nueva_fecha, nuevo_monto, nuevo_comentario)

    def eliminar_abono(self, pago_ids: List[int]) -> bool:
        """Delete payment records."""
        return self.db.eliminar_abono(pago_ids)

    def obtener_abono_por_id(self, pago_id: int) -> Optional[Dict[str, Any]]:
        """Get payment by ID."""
        return self.db.obtener_abono_por_id(pago_id)

    def obtener_lista_abonos(self, proyecto_id: int, filtros: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Get list of payments with filters."""
        return self.db.obtener_lista_abonos(proyecto_id, filtros)

    # --- DASHBOARD & KPI METHODS ---
    def obtener_kpis_dashboard(self, proyecto_id: int, anio: int, mes: int, equipo_id: Optional[int] = None) -> Dict[str, Any]:
        """Get KPIs for dashboard."""
        return self.db.obtener_kpis_dashboard(proyecto_id, anio, mes, equipo_id)

    # --- UTILITY METHODS ---
    def crear_tablas_nucleo(self) -> None:
        """Create core database tables."""
        self.db.crear_tablas_nucleo()

    def asegurar_tabla_pagos(self) -> None:
        """Ensure payments table exists."""
        self.db.asegurar_tabla_pagos()

    def asegurar_tabla_mantenimientos(self) -> None:
        """Ensure maintenance table exists."""
        self.db.asegurar_tabla_mantenimientos()

    def asegurar_tabla_alquiler_meta(self) -> None:
        """Ensure rental metadata table exists."""
        self.db.asegurar_tabla_alquiler_meta()

    # --- ADDITIONAL UTILITY METHODS (passthrough to DatabaseManager) ---
    def obtener_detalles_alquiler(self, transaccion_id: str) -> Optional[Dict[str, Any]]:
        """Get rental details by transaction ID."""
        return self.db.obtener_detalles_alquiler(transaccion_id)

    def obtener_equipos_por_proyecto(self, proyecto_id: int) -> List[Dict[str, Any]]:
        """Get equipment by project."""
        return self.db.obtener_equipos_por_proyecto(proyecto_id)

    def obtener_todos_los_equipos(self) -> List[Dict[str, Any]]:
        """Get all equipment."""
        return self.db.obtener_todos_los_equipos()

    def obtener_transacciones_pendientes_cliente(self, proyecto_id: int, cliente_id: int) -> List[Dict[str, Any]]:
        """Get pending transactions for a client."""
        return self.db.obtener_transacciones_pendientes_cliente(proyecto_id, cliente_id)

    def obtener_fecha_primera_transaccion(self, proyecto_id: int) -> Optional[str]:
        """Get date of first transaction for a project."""
        return self.db.obtener_fecha_primera_transaccion(proyecto_id)

    def obtener_fecha_primera_transaccion_cliente(self, proyecto_id: int, cliente_id: int) -> Optional[str]:
        """Get date of first transaction for a client."""
        return self.db.obtener_fecha_primera_transaccion_cliente(proyecto_id, cliente_id)

    def obtener_fecha_primera_transaccion_operador(self, proyecto_id: int, operador_id: int) -> Optional[str]:
        """Get date of first transaction for an operator."""
        return self.db.obtener_fecha_primera_transaccion_operador(proyecto_id, operador_id)

    def listar_cuentas(self) -> List[Dict[str, Any]]:
        """List all accounts."""
        return self.db.listar_cuentas()

    def obtener_estado_mantenimiento_equipos(self, proyecto_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Get maintenance status for equipment."""
        return self.db.obtener_estado_mantenimiento_equipos(proyecto_id)

    def obtener_acumulado_equipo(self, equipo_id: int, tipo: str) -> float:
        """Get accumulated value for equipment (hours/km)."""
        return self.db.obtener_acumulado_equipo(equipo_id, tipo)

    def actualizar_intervalo_equipo(self, equipo_id: int, tipo: str, valor: float) -> bool:
        """Update equipment interval."""
        return self.db.actualizar_intervalo_equipo(equipo_id, tipo, valor)

    def sembrar_datos_iniciales(self) -> None:
        """Seed initial data."""
        self.db.sembrar_datos_iniciales()

    def crear_tabla_equipos(self) -> None:
        """Create equipment table."""
        self.db.crear_tabla_equipos()

    def asegurar_tablas_mantenimiento(self) -> None:
        """Ensure maintenance tables exist."""
        self.db.asegurar_tablas_mantenimiento()

    def crear_indices(self) -> None:
        """Create database indices."""
        self.db.crear_indices()

    def asegurar_tabla_equipos_entidades(self) -> None:
        """Ensure equipment entities table exists."""
        if hasattr(self.db, 'asegurar_tabla_equipos_entidades'):
            self.db.asegurar_tabla_equipos_entidades()

    def guardar_entidad(self, datos: Dict[str, Any], entidad_id: Optional[int] = None) -> bool:
        """Save or update entity (Cliente/Operador)."""
        if hasattr(self.db, 'guardar_entidad'):
            return self.db.guardar_entidad(datos, entidad_id)
        return False

    def eliminar_entidad(self, entidad_id: int) -> bool:
        """Delete entity."""
        if hasattr(self.db, 'eliminar_entidad'):
            return self.db.eliminar_entidad(entidad_id)
        return False

    def obtener_entidad_por_id(self, entidad_id: int) -> Optional[Dict[str, Any]]:
        """Get entity by ID."""
        if hasattr(self.db, 'obtener_entidad_por_id'):
            return self.db.obtener_entidad_por_id(entidad_id)
        return None
