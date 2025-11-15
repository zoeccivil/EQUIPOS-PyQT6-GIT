"""
Firestore repository implementation using Firebase Authentication with email/password.

This repository uses Firebase REST API for authentication and Firestore for data storage.
No service account JSON required - authentication is done via email/password.
"""
import logging
from typing import List, Dict, Any, Optional
from datetime import date, datetime
import requests
import json

from app.repo.base_repository import BaseRepository

logger = logging.getLogger(__name__)

# Firebase REST API endpoints
FIREBASE_AUTH_URL = "https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword"
FIRESTORE_BASE_URL = "https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)/documents"


class FirestoreRepository(BaseRepository):
    """
    Repository implementation using Firestore as backend.
    
    Authentication is done via Firebase email/password (not service account JSON).
    Uses Firebase REST API for authentication and Firestore REST API for data access.
    """
    
    def __init__(self, project_id: str, email: str, password: str, api_key: str):
        """
        Initialize Firestore repository with email/password authentication.
        
        Args:
            project_id: Firebase project ID
            email: Firebase user email
            password: Firebase user password
            api_key: Firebase Web API key (from Firebase console)
        """
        self.project_id = project_id
        self.email = email
        self.password = password
        self.api_key = api_key
        self.id_token = None
        self.refresh_token = None
        self.base_url = FIRESTORE_BASE_URL.format(project_id=project_id)
        
        # Authenticate on initialization
        self._authenticate()
    
    def _authenticate(self) -> None:
        """
        Authenticate with Firebase using email/password.
        
        Raises:
            ConnectionError: If authentication fails
        """
        try:
            auth_url = f"{FIREBASE_AUTH_URL}?key={self.api_key}"
            payload = {
                "email": self.email,
                "password": self.password,
                "returnSecureToken": True
            }
            
            response = requests.post(auth_url, json=payload)
            response.raise_for_status()
            
            data = response.json()
            self.id_token = data.get("idToken")
            self.refresh_token = data.get("refreshToken")
            
            if not self.id_token:
                raise ConnectionError("No se recibió token de autenticación")
            
            logger.info(f"Autenticación exitosa para {self.email} en proyecto {self.project_id}")
            
        except requests.exceptions.RequestException as e:
            error_msg = f"Error de autenticación Firestore: {e}"
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                    error_msg += f" - {error_detail}"
                except:
                    pass
            logger.error(error_msg)
            raise ConnectionError(error_msg)
    
    def _get_headers(self) -> Dict[str, str]:
        """Get headers for Firestore requests with authentication token."""
        if not self.id_token:
            self._authenticate()
        return {
            "Authorization": f"Bearer {self.id_token}",
            "Content-Type": "application/json"
        }
    
    def _firestore_request(self, method: str, path: str, data: Optional[Dict] = None) -> Any:
        """
        Make a request to Firestore REST API.
        
        Args:
            method: HTTP method (GET, POST, PATCH, DELETE)
            path: Path after base URL (e.g., "proyectos/doc1")
            data: Optional data for POST/PATCH requests
        
        Returns:
            Response JSON data
        """
        url = f"{self.base_url}/{path}"
        headers = self._get_headers()
        
        try:
            if method == "GET":
                response = requests.get(url, headers=headers)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=data)
            elif method == "PATCH":
                response = requests.patch(url, headers=headers, json=data)
            elif method == "DELETE":
                response = requests.delete(url, headers=headers)
            else:
                raise ValueError(f"Método HTTP no soportado: {method}")
            
            response.raise_for_status()
            return response.json() if response.content else {}
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error en request Firestore {method} {path}: {e}")
            raise
    
    def _convert_firestore_doc(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert Firestore document format to simple dict.
        
        Firestore stores values in format: {"field": {"stringValue": "value"}}
        This converts to: {"field": "value"}
        """
        if not doc or "fields" not in doc:
            return {}
        
        result = {}
        fields = doc["fields"]
        
        for key, value_obj in fields.items():
            # Extract value based on type
            if "stringValue" in value_obj:
                result[key] = value_obj["stringValue"]
            elif "integerValue" in value_obj:
                result[key] = int(value_obj["integerValue"])
            elif "doubleValue" in value_obj:
                result[key] = float(value_obj["doubleValue"])
            elif "booleanValue" in value_obj:
                result[key] = value_obj["booleanValue"]
            elif "timestampValue" in value_obj:
                result[key] = value_obj["timestampValue"]
            elif "nullValue" in value_obj:
                result[key] = None
            else:
                result[key] = value_obj
        
        # Add document ID if present
        if "name" in doc:
            doc_id = doc["name"].split("/")[-1]
            result["_firestore_id"] = doc_id
        
        return result
    
    def _convert_to_firestore_fields(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert simple dict to Firestore document format.
        
        Converts: {"field": "value"}
        To: {"fields": {"field": {"stringValue": "value"}}}
        """
        fields = {}
        
        for key, value in data.items():
            if value is None:
                fields[key] = {"nullValue": None}
            elif isinstance(value, bool):
                fields[key] = {"booleanValue": value}
            elif isinstance(value, int):
                fields[key] = {"integerValue": str(value)}
            elif isinstance(value, float):
                fields[key] = {"doubleValue": value}
            elif isinstance(value, str):
                fields[key] = {"stringValue": value}
            elif isinstance(value, (date, datetime)):
                fields[key] = {"timestampValue": value.isoformat()}
            else:
                # Try to convert to string as fallback
                fields[key] = {"stringValue": str(value)}
        
        return {"fields": fields}
    
    # --- PROYECTOS ---
    def obtener_proyectos(self) -> List[Dict[str, Any]]:
        """Obtener todos los proyectos."""
        try:
            response = self._firestore_request("GET", "proyectos")
            documents = response.get("documents", [])
            return [self._convert_firestore_doc(doc) for doc in documents]
        except Exception as e:
            logger.error(f"Error obteniendo proyectos: {e}")
            return []
    
    def obtener_proyecto_por_id(self, proyecto_id: int) -> Optional[Dict[str, Any]]:
        """Obtener un proyecto por su ID."""
        try:
            response = self._firestore_request("GET", f"proyectos/{proyecto_id}")
            return self._convert_firestore_doc(response)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return None
            raise
    
    def crear_proyecto(self, nombre: str, descripcion: str = "", 
                       moneda: str = "RD$", cuenta_principal: str = "") -> int:
        """Crear un nuevo proyecto."""
        # Generate ID (in production, use auto-increment or UUID)
        proyectos = self.obtener_proyectos()
        nuevo_id = max([p.get("id", 0) for p in proyectos], default=0) + 1
        
        data = self._convert_to_firestore_fields({
            "id": nuevo_id,
            "nombre": nombre,
            "descripcion": descripcion,
            "moneda": moneda,
            "cuenta_principal": cuenta_principal
        })
        
        self._firestore_request("PATCH", f"proyectos/{nuevo_id}", data)
        return nuevo_id
    
    # --- EQUIPOS ---
    def obtener_equipos(self, proyecto_id: Optional[int] = None, 
                        activo: Optional[bool] = None) -> List[Dict[str, Any]]:
        """Obtener equipos, opcionalmente filtrados por proyecto y estado activo."""
        try:
            response = self._firestore_request("GET", "equipos")
            documents = response.get("documents", [])
            equipos = [self._convert_firestore_doc(doc) for doc in documents]
            
            # Apply filters
            if proyecto_id is not None:
                equipos = [e for e in equipos if e.get("proyecto_id") == proyecto_id]
            if activo is not None:
                equipos = [e for e in equipos if e.get("activo", True) == activo]
            
            return equipos
        except Exception as e:
            logger.error(f"Error obteniendo equipos: {e}")
            return []
    
    def obtener_equipo_por_id(self, equipo_id: int) -> Optional[Dict[str, Any]]:
        """Obtener un equipo por su ID."""
        try:
            response = self._firestore_request("GET", f"equipos/{equipo_id}")
            return self._convert_firestore_doc(response)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return None
            raise
    
    def crear_equipo(self, proyecto_id: int, nombre: str, marca: str = "",
                     modelo: str = "", categoria: str = "", equipo: str = "") -> int:
        """Crear un nuevo equipo."""
        equipos = self.obtener_equipos()
        nuevo_id = max([e.get("id", 0) for e in equipos], default=0) + 1
        
        data = self._convert_to_firestore_fields({
            "id": nuevo_id,
            "proyecto_id": proyecto_id,
            "nombre": nombre,
            "marca": marca,
            "modelo": modelo,
            "categoria": categoria,
            "equipo": equipo,
            "activo": True
        })
        
        self._firestore_request("PATCH", f"equipos/{nuevo_id}", data)
        return nuevo_id
    
    def actualizar_equipo(self, equipo_id: int, datos: Dict[str, Any]) -> bool:
        """Actualizar datos de un equipo."""
        try:
            data = self._convert_to_firestore_fields(datos)
            self._firestore_request("PATCH", f"equipos/{equipo_id}?updateMask.fieldPaths=" + 
                                   ",".join(datos.keys()), data)
            return True
        except Exception as e:
            logger.error(f"Error actualizando equipo {equipo_id}: {e}")
            return False
    
    # --- CLIENTES ---
    def obtener_clientes(self) -> List[Dict[str, Any]]:
        """Obtener todos los clientes."""
        try:
            response = self._firestore_request("GET", "clientes")
            documents = response.get("documents", [])
            return [self._convert_firestore_doc(doc) for doc in documents]
        except Exception as e:
            logger.error(f"Error obteniendo clientes: {e}")
            return []
    
    def obtener_cliente_por_id(self, cliente_id: int) -> Optional[Dict[str, Any]]:
        """Obtener un cliente por su ID."""
        try:
            response = self._firestore_request("GET", f"clientes/{cliente_id}")
            return self._convert_firestore_doc(response)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return None
            raise
    
    def crear_cliente(self, nombre: str, **kwargs) -> int:
        """Crear un nuevo cliente."""
        clientes = self.obtener_clientes()
        nuevo_id = max([c.get("id", 0) for c in clientes], default=0) + 1
        
        datos = {"id": nuevo_id, "nombre": nombre}
        datos.update(kwargs)
        
        data = self._convert_to_firestore_fields(datos)
        self._firestore_request("PATCH", f"clientes/{nuevo_id}", data)
        return nuevo_id
    
    # --- OPERADORES ---
    def obtener_operadores(self) -> List[Dict[str, Any]]:
        """Obtener todos los operadores."""
        try:
            response = self._firestore_request("GET", "operadores")
            documents = response.get("documents", [])
            return [self._convert_firestore_doc(doc) for doc in documents]
        except Exception as e:
            logger.error(f"Error obteniendo operadores: {e}")
            return []
    
    def obtener_operador_por_id(self, operador_id: int) -> Optional[Dict[str, Any]]:
        """Obtener un operador por su ID."""
        try:
            response = self._firestore_request("GET", f"operadores/{operador_id}")
            return self._convert_firestore_doc(response)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return None
            raise
    
    def crear_operador(self, nombre: str, **kwargs) -> int:
        """Crear un nuevo operador."""
        operadores = self.obtener_operadores()
        nuevo_id = max([o.get("id", 0) for o in operadores], default=0) + 1
        
        datos = {"id": nuevo_id, "nombre": nombre}
        datos.update(kwargs)
        
        data = self._convert_to_firestore_fields(datos)
        self._firestore_request("PATCH", f"operadores/{nuevo_id}", data)
        return nuevo_id
    
    # --- ALQUILERES ---
    def obtener_alquileres(self, proyecto_id: Optional[int] = None,
                          fecha_inicio: Optional[date] = None,
                          fecha_fin: Optional[date] = None,
                          cliente_id: Optional[int] = None,
                          equipo_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Obtener alquileres con filtros opcionales."""
        try:
            response = self._firestore_request("GET", "alquileres")
            documents = response.get("documents", [])
            alquileres = [self._convert_firestore_doc(doc) for doc in documents]
            
            # Apply filters (basic client-side filtering)
            if proyecto_id is not None:
                alquileres = [a for a in alquileres if a.get("proyecto_id") == proyecto_id]
            if cliente_id is not None:
                alquileres = [a for a in alquileres if a.get("cliente_id") == cliente_id]
            if equipo_id is not None:
                alquileres = [a for a in alquileres if a.get("equipo_id") == equipo_id]
            # Date filtering would require parsing ISO dates
            
            return alquileres
        except Exception as e:
            logger.error(f"Error obteniendo alquileres: {e}")
            return []
    
    def obtener_alquiler_por_id(self, alquiler_id: str) -> Optional[Dict[str, Any]]:
        """Obtener un alquiler por su ID."""
        try:
            response = self._firestore_request("GET", f"alquileres/{alquiler_id}")
            return self._convert_firestore_doc(response)
        except requests.exceptions.HTTPError as e:
            if e.response.status_code == 404:
                return None
            raise
    
    def crear_alquiler(self, datos: Dict[str, Any]) -> str:
        """Crear un nuevo alquiler. Retorna el ID del alquiler creado."""
        import uuid
        alquiler_id = datos.get("id", str(uuid.uuid4()))
        
        data = self._convert_to_firestore_fields(datos)
        self._firestore_request("PATCH", f"alquileres/{alquiler_id}", data)
        return alquiler_id
    
    def actualizar_alquiler(self, alquiler_id: str, datos: Dict[str, Any]) -> bool:
        """Actualizar datos de un alquiler."""
        try:
            data = self._convert_to_firestore_fields(datos)
            self._firestore_request("PATCH", f"alquileres/{alquiler_id}?updateMask.fieldPaths=" + 
                                   ",".join(datos.keys()), data)
            return True
        except Exception as e:
            logger.error(f"Error actualizando alquiler {alquiler_id}: {e}")
            return False
    
    def eliminar_alquiler(self, alquiler_id: str) -> bool:
        """Eliminar un alquiler."""
        try:
            self._firestore_request("DELETE", f"alquileres/{alquiler_id}")
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
        try:
            response = self._firestore_request("GET", "transacciones")
            documents = response.get("documents", [])
            transacciones = [self._convert_firestore_doc(doc) for doc in documents]
            
            if proyecto_id is not None:
                transacciones = [t for t in transacciones if t.get("proyecto_id") == proyecto_id]
            if tipo is not None:
                transacciones = [t for t in transacciones if t.get("tipo") == tipo]
            
            return transacciones
        except Exception as e:
            logger.error(f"Error obteniendo transacciones: {e}")
            return []
    
    def crear_transaccion(self, datos: Dict[str, Any]) -> str:
        """Crear una nueva transacción."""
        import uuid
        transaccion_id = datos.get("id", str(uuid.uuid4()))
        
        data = self._convert_to_firestore_fields(datos)
        self._firestore_request("PATCH", f"transacciones/{transaccion_id}", data)
        return transaccion_id
    
    # --- PAGOS ---
    def obtener_pagos(self, proyecto_id: Optional[int] = None,
                     operador_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Obtener pagos con filtros opcionales."""
        try:
            response = self._firestore_request("GET", "pagos")
            documents = response.get("documents", [])
            pagos = [self._convert_firestore_doc(doc) for doc in documents]
            
            if proyecto_id is not None:
                pagos = [p for p in pagos if p.get("proyecto_id") == proyecto_id]
            if operador_id is not None:
                pagos = [p for p in pagos if p.get("operador_id") == operador_id]
            
            return pagos
        except Exception as e:
            logger.error(f"Error obteniendo pagos: {e}")
            return []
    
    def crear_pago(self, datos: Dict[str, Any]) -> int:
        """Crear un nuevo pago."""
        pagos = self.obtener_pagos()
        nuevo_id = max([p.get("id", 0) for p in pagos], default=0) + 1
        
        datos["id"] = nuevo_id
        data = self._convert_to_firestore_fields(datos)
        self._firestore_request("PATCH", f"pagos/{nuevo_id}", data)
        return nuevo_id
    
    # --- MANTENIMIENTOS ---
    def obtener_mantenimientos(self, equipo_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """Obtener mantenimientos, opcionalmente filtrados por equipo."""
        try:
            response = self._firestore_request("GET", "mantenimientos")
            documents = response.get("documents", [])
            mantenimientos = [self._convert_firestore_doc(doc) for doc in documents]
            
            if equipo_id is not None:
                mantenimientos = [m for m in mantenimientos if m.get("equipo_id") == equipo_id]
            
            return mantenimientos
        except Exception as e:
            logger.error(f"Error obteniendo mantenimientos: {e}")
            return []
    
    def crear_mantenimiento(self, datos: Dict[str, Any]) -> int:
        """Crear un nuevo registro de mantenimiento."""
        mantenimientos = self.obtener_mantenimientos()
        nuevo_id = max([m.get("id", 0) for m in mantenimientos], default=0) + 1
        
        datos["id"] = nuevo_id
        data = self._convert_to_firestore_fields(datos)
        self._firestore_request("PATCH", f"mantenimientos/{nuevo_id}", data)
        return nuevo_id
    
    # --- CATEGORÍAS ---
    def obtener_categorias(self) -> List[Dict[str, Any]]:
        """Obtener todas las categorías."""
        try:
            response = self._firestore_request("GET", "categorias")
            documents = response.get("documents", [])
            return [self._convert_firestore_doc(doc) for doc in documents]
        except Exception as e:
            logger.error(f"Error obteniendo categorías: {e}")
            return []
    
    # --- CUENTAS ---
    def obtener_cuentas(self) -> List[Dict[str, Any]]:
        """Obtener todas las cuentas."""
        try:
            response = self._firestore_request("GET", "cuentas")
            documents = response.get("documents", [])
            return [self._convert_firestore_doc(doc) for doc in documents]
        except Exception as e:
            logger.error(f"Error obteniendo cuentas: {e}")
            return []
    
    # --- HEALTH CHECK ---
    def verificar_conexion(self) -> bool:
        """Verificar que la conexión al backend está activa."""
        try:
            # Try to get a simple collection
            self._firestore_request("GET", "proyectos")
            return True
        except Exception as e:
            logger.error(f"Error verificando conexión Firestore: {e}")
            return False
    
    def cerrar(self) -> None:
        """Cerrar conexiones y liberar recursos."""
        # REST API doesn't require explicit cleanup
        logger.info("Cerrando conexión Firestore")
        self.id_token = None
        self.refresh_token = None
