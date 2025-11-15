"""
Repository factory for creating data source instances.

Centralizes repository creation based on configuration.
"""
import logging
from typing import Optional

from app.app_settings import AppSettings
from app.repo.base_repository import BaseRepository
from app.repo.firestore_repository import FirestoreRepository
from app.repo.sqlite_repository import SQLiteRepository

logger = logging.getLogger(__name__)


class RepositoryFactory:
    """
    Factory for creating repository instances based on configuration.
    """
    
    @staticmethod
    def create_from_settings(settings: AppSettings) -> Optional[BaseRepository]:
        """
        Create a repository instance based on app settings.
        
        Args:
            settings: AppSettings instance with configuration
        
        Returns:
            Repository instance or None if creation fails
        
        Raises:
            ConnectionError: If Firestore authentication fails
            ValueError: If configuration is invalid
        """
        data_source = settings.get_data_source()
        
        if data_source == "firestore":
            return RepositoryFactory.create_firestore(settings)
        elif data_source == "sqlite":
            return RepositoryFactory.create_sqlite(settings)
        else:
            raise ValueError(f"Data source no soportado: {data_source}")
    
    @staticmethod
    def create_firestore(settings: AppSettings) -> FirestoreRepository:
        """
        Create a Firestore repository instance.
        
        Args:
            settings: AppSettings instance with Firestore configuration
        
        Returns:
            FirestoreRepository instance
        
        Raises:
            ConnectionError: If authentication fails
            ValueError: If configuration is incomplete
        """
        config = settings.get_firestore_config()
        
        # Validate configuration
        if not config.get("project_id"):
            raise ValueError("Firestore project_id no configurado")
        if not config.get("email"):
            raise ValueError("Firestore email no configurado")
        if not config.get("password"):
            raise ValueError("Firestore password no configurado")
        if not config.get("api_key"):
            raise ValueError("Firestore api_key no configurado")
        
        logger.info(f"Creando FirestoreRepository para proyecto: {config['project_id']}")
        
        try:
            repo = FirestoreRepository(
                project_id=config["project_id"],
                email=config["email"],
                password=config["password"],
                api_key=config["api_key"]
            )
            
            # Verify connection
            if not repo.verificar_conexion():
                raise ConnectionError("No se pudo verificar la conexión a Firestore")
            
            logger.info("FirestoreRepository creado y verificado exitosamente")
            return repo
            
        except Exception as e:
            logger.error(f"Error creando FirestoreRepository: {e}")
            raise ConnectionError(f"Error conectando a Firestore: {e}")
    
    @staticmethod
    def create_sqlite(settings: AppSettings, db_path: Optional[str] = None) -> SQLiteRepository:
        """
        Create a SQLite repository instance.
        
        Args:
            settings: AppSettings instance with SQLite configuration
            db_path: Optional explicit database path (overrides settings)
        
        Returns:
            SQLiteRepository instance
        """
        if db_path is None:
            db_path = settings.get_sqlite_path()
        
        logger.info(f"Creando SQLiteRepository con path: {db_path}")
        
        try:
            repo = SQLiteRepository(db_path)
            
            # Verify connection
            if not repo.verificar_conexion():
                raise ConnectionError(f"No se pudo conectar a SQLite en {db_path}")
            
            logger.info("SQLiteRepository creado exitosamente")
            return repo
            
        except Exception as e:
            logger.error(f"Error creando SQLiteRepository: {e}")
            raise
    
    @staticmethod
    def create_sqlite_for_migration(db_path: str) -> SQLiteRepository:
        """
        Create a SQLite repository for migration purposes.
        
        This is a convenience method for creating SQLite repositories
        when doing data migrations, without needing full settings.
        
        Args:
            db_path: Path to SQLite database file
        
        Returns:
            SQLiteRepository instance
        """
        logger.info(f"Creando SQLiteRepository para migración: {db_path}")
        return SQLiteRepository(db_path)
    
    @staticmethod
    def create_sqlite_for_backup(backup_path: str) -> SQLiteRepository:
        """
        Create a SQLite repository for backup purposes.
        
        Args:
            backup_path: Path for the backup database file
        
        Returns:
            SQLiteRepository instance
        """
        logger.info(f"Creando SQLiteRepository para backup: {backup_path}")
        
        # Create a new database for the backup
        repo = SQLiteRepository(backup_path)
        
        # Initialize tables for the backup
        try:
            repo.db.crear_tablas_nucleo()
            repo.db.crear_tabla_equipos()
            repo.db.asegurar_tabla_alquiler_meta()
            repo.db.asegurar_tabla_pagos()
            repo.db.asegurar_tabla_mantenimientos()
            repo.db.asegurar_tablas_mantenimiento()
            logger.info("Tablas de backup creadas exitosamente")
        except Exception as e:
            logger.error(f"Error creando tablas de backup: {e}")
            raise
        
        return repo
