"""
Lector de datos de SQLite.

Maneja la lectura de datos desde la base de datos SQLite,
incluyendo validación y transformación inicial de datos.
"""
import sqlite3
import logging
from typing import List, Dict, Any, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class SQLiteReaderError(Exception):
    """Excepción para errores del lector de SQLite"""
    pass


class SQLiteReader:
    """
    Lee datos de la base de datos SQLite.
    """
    
    def __init__(self, db_path: str):
        """
        Inicializa el lector.
        
        Args:
            db_path: Ruta a la base de datos SQLite
        """
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None
    
    def connect(self):
        """Establece conexión con la base de datos"""
        try:
            self.conn = sqlite3.connect(self.db_path)
            self.conn.row_factory = sqlite3.Row
            logger.info(f"Connected to SQLite database: {self.db_path}")
        except Exception as e:
            raise SQLiteReaderError(f"Failed to connect to database: {e}")
    
    def disconnect(self):
        """Cierra la conexión"""
        if self.conn:
            self.conn.close()
            logger.info("Disconnected from SQLite database")
    
    def get_table_names(self) -> List[str]:
        """
        Obtiene lista de nombres de tablas en la base de datos.
        
        Returns:
            Lista de nombres de tablas
        """
        if not self.conn:
            raise SQLiteReaderError("Not connected to database")
        
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' "
            "AND name NOT LIKE 'sqlite_%'"
        )
        tables = [row[0] for row in cursor.fetchall()]
        logger.debug(f"Found tables: {tables}")
        return tables
    
    def get_table_schema(self, table_name: str) -> List[Dict[str, Any]]:
        """
        Obtiene el esquema de una tabla.
        
        Args:
            table_name: Nombre de la tabla
            
        Returns:
            Lista de diccionarios con información de columnas
        """
        if not self.conn:
            raise SQLiteReaderError("Not connected to database")
        
        cursor = self.conn.cursor()
        cursor.execute(f"PRAGMA table_info({table_name})")
        columns = []
        for row in cursor.fetchall():
            columns.append({
                'cid': row[0],
                'name': row[1],
                'type': row[2],
                'notnull': row[3],
                'default': row[4],
                'pk': row[5]
            })
        logger.debug(f"Schema for {table_name}: {len(columns)} columns")
        return columns
    
    def count_records(self, table_name: str) -> int:
        """
        Cuenta registros en una tabla.
        
        Args:
            table_name: Nombre de la tabla
            
        Returns:
            Número de registros
        """
        if not self.conn:
            raise SQLiteReaderError("Not connected to database")
        
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
        count = cursor.fetchone()[0]
        logger.debug(f"Table {table_name} has {count} records")
        return count
    
    def read_all_records(self, table_name: str) -> List[Dict[str, Any]]:
        """
        Lee todos los registros de una tabla.
        
        Args:
            table_name: Nombre de la tabla
            
        Returns:
            Lista de registros como diccionarios
        """
        if not self.conn:
            raise SQLiteReaderError("Not connected to database")
        
        cursor = self.conn.cursor()
        cursor.execute(f"SELECT * FROM {table_name}")
        records = [dict(row) for row in cursor.fetchall()]
        logger.info(f"Read {len(records)} records from {table_name}")
        return records
    
    def read_records_batch(
        self,
        table_name: str,
        batch_size: int,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Lee registros en lotes.
        
        Args:
            table_name: Nombre de la tabla
            batch_size: Tamaño del lote
            offset: Offset para paginación
            
        Returns:
            Lista de registros como diccionarios
        """
        if not self.conn:
            raise SQLiteReaderError("Not connected to database")
        
        cursor = self.conn.cursor()
        cursor.execute(
            f"SELECT * FROM {table_name} LIMIT {batch_size} OFFSET {offset}"
        )
        records = [dict(row) for row in cursor.fetchall()]
        logger.debug(
            f"Read batch from {table_name}: {len(records)} records "
            f"(offset {offset})"
        )
        return records
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()
