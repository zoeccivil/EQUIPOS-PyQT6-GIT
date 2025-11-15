"""
Base repository interface for data access layer.

This abstract base class defines the contract that all repository
implementations must follow, whether backed by Firestore, SQLite, or other data sources.
"""
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional
from datetime import date


class BaseRepository(ABC):
    """Abstract base class for all repository implementations."""
    
    # --- PROYECTOS ---
    @abstractmethod
    def obtener_proyectos(self) -> List[Dict[str, Any]]:
        """Obtener todos los proyectos."""
        pass
    
    @abstractmethod
    def obtener_proyecto_por_id(self, proyecto_id: int) -> Optional[Dict[str, Any]]:
        """Obtener un proyecto por su ID."""
        pass
    
    @abstractmethod
    def crear_proyecto(self, nombre: str, descripcion: str = "", 
                       moneda: str = "RD$", cuenta_principal: str = "") -> int:
        """Crear un nuevo proyecto."""
        pass
    
    # --- EQUIPOS ---
    @abstractmethod
    def obtener_equipos(self, proyecto_id: Optional[int] = None, 
                        activo: Optional[bool] = None) -> List[Dict[str, Any]]:
        """Obtener equipos, opcionalmente filtrados por proyecto y estado activo."""
        pass
    
    @abstractmethod
    def obtener_equipo_por_id(self, equipo_id: int) -> Optional[Dict[str, Any]]:
        """Obtener un equipo por su ID."""
        pass
    
    @abstractmethod
    def crear_equipo(self, proyecto_id: int, nombre: str, marca: str = "",
                     modelo: str = "", categoria: str = "", equipo: str = "") -> int:
        """Crear un nuevo equipo."""
        pass
    
    @abstractmethod
    def actualizar_equipo(self, equipo_id: int, datos: Dict[str, Any]) -> bool:
        """Actualizar datos de un equipo."""
        pass
    
    # --- CLIENTES ---
    @abstractmethod
    def obtener_clientes(self) -> List[Dict[str, Any]]:
        """Obtener todos los clientes."""
        pass
    
    @abstractmethod
    def obtener_cliente_por_id(self, cliente_id: int) -> Optional[Dict[str, Any]]:
        """Obtener un cliente por su ID."""
        pass
    
    @abstractmethod
    def crear_cliente(self, nombre: str, **kwargs) -> int:
        """Crear un nuevo cliente."""
        pass
    
    # --- OPERADORES ---
    @abstractmethod
    def obtener_operadores(self) -> List[Dict[str, Any]]:
        """Obtener todos los operadores."""
        pass
    
    @abstractmethod
    def obtener_operador_por_id(self, operador_id: int) -> Optional[Dict[str, Any]]:
        """Obtener un operador por su ID."""
        pass
    
    @abstractmethod
    def crear_operador(self, nombre: str, **kwargs) -> int:
        """Crear un nuevo operador."""
        pass
    
    # --- ALQUILERES ---
    @abstractmethod
    def obtener_alquileres(self, proyecto_id: Optional[int] = None,
                          fecha_inicio: Optional[date] = None,
                          fecha_fin: Optional[date] = None,
                          cliente_id: Optional[int] = None,
                          equipo_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Obtener alquileres con filtros opcionales."""
        pass
    
    @abstractmethod
    def obtener_alquiler_por_id(self, alquiler_id: str) -> Optional[Dict[str, Any]]:
        """Obtener un alquiler por su ID."""
        pass
    
    @abstractmethod
    def crear_alquiler(self, datos: Dict[str, Any]) -> str:
        """Crear un nuevo alquiler. Retorna el ID del alquiler creado."""
        pass
    
    @abstractmethod
    def actualizar_alquiler(self, alquiler_id: str, datos: Dict[str, Any]) -> bool:
        """Actualizar datos de un alquiler."""
        pass
    
    @abstractmethod
    def eliminar_alquiler(self, alquiler_id: str) -> bool:
        """Eliminar un alquiler."""
        pass
    
    # --- TRANSACCIONES ---
    @abstractmethod
    def obtener_transacciones(self, proyecto_id: Optional[int] = None,
                             tipo: Optional[str] = None,
                             fecha_inicio: Optional[date] = None,
                             fecha_fin: Optional[date] = None) -> List[Dict[str, Any]]:
        """Obtener transacciones con filtros opcionales."""
        pass
    
    @abstractmethod
    def crear_transaccion(self, datos: Dict[str, Any]) -> str:
        """Crear una nueva transacción."""
        pass
    
    # --- PAGOS ---
    @abstractmethod
    def obtener_pagos(self, proyecto_id: Optional[int] = None,
                     operador_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Obtener pagos con filtros opcionales."""
        pass
    
    @abstractmethod
    def crear_pago(self, datos: Dict[str, Any]) -> int:
        """Crear un nuevo pago."""
        pass
    
    # --- MANTENIMIENTOS ---
    @abstractmethod
    def obtener_mantenimientos(self, equipo_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Obtener mantenimientos, opcionalmente filtrados por equipo."""
        pass
    
    @abstractmethod
    def crear_mantenimiento(self, datos: Dict[str, Any]) -> int:
        """Crear un nuevo registro de mantenimiento."""
        pass
    
    # --- CATEGORÍAS ---
    @abstractmethod
    def obtener_categorias(self) -> List[Dict[str, Any]]:
        """Obtener todas las categorías."""
        pass
    
    # --- CUENTAS ---
    @abstractmethod
    def obtener_cuentas(self) -> List[Dict[str, Any]]:
        """Obtener todas las cuentas."""
        pass
    
    # --- HEALTH CHECK ---
    @abstractmethod
    def verificar_conexion(self) -> bool:
        """Verificar que la conexión al backend está activa."""
        pass
    
    @abstractmethod
    def cerrar(self) -> None:
        """Cerrar conexiones y liberar recursos."""
        pass
