"""
Mapeador de IDs entre SQLite y Firestore.

Mantiene un registro de la correspondencia entre IDs de SQLite
y document IDs de Firestore para mantener referencias.
"""
import json
import logging
from typing import Dict, Optional, Any
from pathlib import Path

logger = logging.getLogger(__name__)


class IDMapper:
    """
    Gestiona el mapeo entre IDs de SQLite y document IDs de Firestore.
    """
    
    def __init__(self, mapping_file: str = "mapping.json"):
        """
        Inicializa el mapeador.
        
        Args:
            mapping_file: Ruta al archivo de mapeo
        """
        self.mapping_file = mapping_file
        self.mappings: Dict[str, str] = {}
        self._load_existing()
    
    def _load_existing(self):
        """Carga mapeos existentes desde archivo si existe"""
        if Path(self.mapping_file).exists():
            try:
                with open(self.mapping_file, 'r') as f:
                    self.mappings = json.load(f)
                logger.info(f"Loaded {len(self.mappings)} existing mappings")
            except Exception as e:
                logger.warning(f"Could not load existing mappings: {e}")
    
    def add_mapping(self, table: str, sqlite_id: Any, firestore_id: str):
        """
        Añade un mapeo.
        
        Args:
            table: Nombre de la tabla
            sqlite_id: ID de SQLite
            firestore_id: Document ID de Firestore
        """
        key = f"{table}_{sqlite_id}"
        self.mappings[key] = firestore_id
        logger.debug(f"Mapped {key} -> {firestore_id}")
    
    def get_firestore_id(self, table: str, sqlite_id: Any) -> Optional[str]:
        """
        Obtiene el document ID de Firestore para un ID de SQLite.
        
        Args:
            table: Nombre de la tabla
            sqlite_id: ID de SQLite
            
        Returns:
            Document ID de Firestore o None si no existe
        """
        key = f"{table}_{sqlite_id}"
        return self.mappings.get(key)
    
    def save(self):
        """Guarda los mapeos a archivo"""
        try:
            with open(self.mapping_file, 'w') as f:
                json.dump(self.mappings, f, indent=2)
            logger.info(f"Saved {len(self.mappings)} mappings to {self.mapping_file}")
        except Exception as e:
            logger.error(f"Failed to save mappings: {e}")
    
    def get_all_mappings(self) -> Dict[str, str]:
        """Retorna todos los mapeos"""
        return self.mappings.copy()
    
    def clear(self):
        """Limpia todos los mapeos"""
        self.mappings.clear()
