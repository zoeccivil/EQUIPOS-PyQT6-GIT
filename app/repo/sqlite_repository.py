"""
SQLite repository adapter.

Wraps the existing DatabaseManager to implement the BaseRepository interface.
This allows the app to work with SQLite through the same interface as Firestore.
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import date

from app.repo.base_repository import BaseRepository
from logic import DatabaseManager

logger = logging.getLogger(__name__)


class SQLiteRepository(BaseRepository):
    """
    Repository implementation backed by SQLite.
    
    This is an adapter that wraps the existing DatabaseManager class
    to provide the BaseRepository interface.
    """
    
    def __init__(self, db_path: str):
        """
        Initialize SQLite repository.
        
        Args:
            db_path: Path to the SQLite database file
        """
        self.db = DatabaseManager(db_path)
        logger.info(f"SQLiteRepository initialized with {db_path}")
    
    # --- PROYECTOS ---
    def obtener_proyectos(self) -> List[Dict[str, Any]]:
        """Obtener todos los proyectos."""
        return self.db.obtener_proyectos()
    
    def obtener_proyecto_por_id(self, proyecto_id: int) -> Optional[Dict[str, Any]]:
        """Obtener un proyecto por su ID."""
        return self.db.obtener_proyecto_por_id(proyecto_id)
    
    def crear_proyecto(self, nombre: str, descripcion: str = "", 
                       moneda: str = "RD$", cuenta_principal: str = "") -> int:
        """Crear un nuevo proyecto."""
        return self.db.crear_proyecto(nombre, descripcion, moneda, cuenta_principal)
    
    # --- EQUIPOS ---
    def obtener_equipos(self, proyecto_id: Optional[int] = None, 
                        activo: Optional[bool] = None) -> List[Dict[str, Any]]:
        """Obtener equipos, opcionalmente filtrados por proyecto y estado activo."""
        equipos = self.db.obtener_equipos_todos()
        
        if proyecto_id is not None:
            equipos = [e for e in equipos if e.get("proyecto_id") == proyecto_id]
        if activo is not None:
            equipos = [e for e in equipos if e.get("activo", 1) == (1 if activo else 0)]
        
        return equipos
    
    def obtener_equipo_por_id(self, equipo_id: int) -> Optional[Dict[str, Any]]:
        """Obtener un equipo por su ID."""
        return self.db.obtener_equipo_por_id(equipo_id)
    
    def crear_equipo(self, proyecto_id: int, nombre: str, marca: str = "",
                     modelo: str = "", categoria: str = "", equipo: str = "") -> int:
        """Crear un nuevo equipo."""
        return self.db.insertar_equipo(proyecto_id, nombre, marca, modelo, categoria, equipo)
    
    def actualizar_equipo(self, equipo_id: int, datos: Dict[str, Any]) -> bool:
        """Actualizar datos de un equipo."""
        try:
            self.db.actualizar_equipo(equipo_id, datos)
            return True
        except Exception as e:
            logger.error(f"Error actualizando equipo {equipo_id}: {e}")
            return False
    
    # --- CLIENTES ---
    def obtener_clientes(self) -> List[Dict[str, Any]]:
        """Obtener todos los clientes."""
        return self.db.obtener_entidades("Cliente")
    
    def obtener_cliente_por_id(self, cliente_id: int) -> Optional[Dict[str, Any]]:
        """Obtener un cliente por su ID."""
        clientes = self.obtener_clientes()
        for cliente in clientes:
            if cliente.get("id") == cliente_id:
                return cliente
        return None
    
    def crear_cliente(self, nombre: str, **kwargs) -> int:
        """Crear un nuevo cliente."""
        return self.db.insertar_entidad("Cliente", nombre, **kwargs)
    
    # --- OPERADORES ---
    def obtener_operadores(self) -> List[Dict[str, Any]]:
        """Obtener todos los operadores."""
        return self.db.obtener_entidades("Operador")
    
    def obtener_operador_por_id(self, operador_id: int) -> Optional[Dict[str, Any]]:
        """Obtener un operador por su ID."""
        operadores = self.obtener_operadores()
        for operador in operadores:
            if operador.get("id") == operador_id:
                return operador
        return None
    
    def crear_operador(self, nombre: str, **kwargs) -> int:
        """Crear un nuevo operador."""
        return self.db.insertar_entidad("Operador", nombre, **kwargs)
    
    # --- ALQUILERES ---
    def obtener_alquileres(self, proyecto_id: Optional[int] = None,
                          fecha_inicio: Optional[date] = None,
                          fecha_fin: Optional[date] = None,
                          cliente_id: Optional[int] = None,
                          equipo_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Obtener alquileres con filtros opcionales."""
        # Use the existing method with filters
        if proyecto_id is not None:
            return self.db.obtener_alquileres(
                proyecto_id=proyecto_id,
                fecha_inicio=fecha_inicio,
                fecha_fin=fecha_fin,
                cliente_id=cliente_id,
                equipo_id=equipo_id
            )
        else:
            # Get all alquileres
            return self.db.obtener_todos_alquileres()
    
    def obtener_alquiler_por_id(self, alquiler_id: str) -> Optional[Dict[str, Any]]:
        """Obtener un alquiler por su ID."""
        return self.db.obtener_alquiler_por_id(alquiler_id)
    
    def crear_alquiler(self, datos: Dict[str, Any]) -> str:
        """Crear un nuevo alquiler. Retorna el ID del alquiler creado."""
        return self.db.insertar_alquiler(datos)
    
    def actualizar_alquiler(self, alquiler_id: str, datos: Dict[str, Any]) -> bool:
        """Actualizar datos de un alquiler."""
        try:
            self.db.actualizar_alquiler(alquiler_id, datos)
            return True
        except Exception as e:
            logger.error(f"Error actualizando alquiler {alquiler_id}: {e}")
            return False
    
    def eliminar_alquiler(self, alquiler_id: str) -> bool:
        """Eliminar un alquiler."""
        try:
            self.db.eliminar_alquiler(alquiler_id)
            return True
        except Exception as e:
            logger.error(f"Error eliminando alquiler {alquiler_id}: {e}")
            return False
    
    # --- TRANSACCIONES ---
    def obtener_transacciones(self, proyecto_id: Optional[int] = None,
                             tipo: Optional[str] = None,
                             fecha_inicio: Optional[date] = None,
                             fecha_fin: Optional[date] = None) -> List[Dict[str, Any]]:
        """Obtener transacciones con filtros opcionales."""
        return self.db.obtener_transacciones(
            proyecto_id=proyecto_id,
            tipo=tipo,
            fecha_inicio=fecha_inicio,
            fecha_fin=fecha_fin
        )
    
    def crear_transaccion(self, datos: Dict[str, Any]) -> str:
        """Crear una nueva transacción."""
        return self.db.insertar_transaccion(datos)
    
    # --- PAGOS ---
    def obtener_pagos(self, proyecto_id: Optional[int] = None,
                     operador_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Obtener pagos con filtros opcionales."""
        return self.db.obtener_pagos(proyecto_id=proyecto_id, operador_id=operador_id)
    
    def crear_pago(self, datos: Dict[str, Any]) -> int:
        """Crear un nuevo pago."""
        return self.db.insertar_pago(datos)
    
    # --- MANTENIMIENTOS ---
    def obtener_mantenimientos(self, equipo_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Obtener mantenimientos, opcionalmente filtrados por equipo."""
        return self.db.obtener_mantenimientos(equipo_id=equipo_id)
    
    def crear_mantenimiento(self, datos: Dict[str, Any]) -> int:
        """Crear un nuevo registro de mantenimiento."""
        return self.db.insertar_mantenimiento(datos)
    
    # --- CATEGORÍAS ---
    def obtener_categorias(self) -> List[Dict[str, Any]]:
        """Obtener todas las categorías."""
        return self.db.obtener_categorias()
    
    # --- CUENTAS ---
    def obtener_cuentas(self) -> List[Dict[str, Any]]:
        """Obtener todas las cuentas."""
        return self.db.obtener_cuentas()
    
    # --- HEALTH CHECK ---
    def verificar_conexion(self) -> bool:
        """Verificar que la conexión al backend está activa."""
        try:
            # Try a simple query
            self.db.obtener_proyectos()
            return True
        except Exception as e:
            logger.error(f"Error verificando conexión SQLite: {e}")
            return False
    
    def cerrar(self) -> None:
        """Cerrar conexiones y liberar recursos."""
        if hasattr(self.db, '_conn') and self.db._conn:
            self.db._conn.close()
            logger.info("Conexión SQLite cerrada")
