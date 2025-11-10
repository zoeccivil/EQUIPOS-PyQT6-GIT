"""
Repository Factory

Provides factory methods to create repository instances based on configuration.
This centralizes repository creation and makes it easy to switch between
SQLite and Firestore implementations.
"""
from typing import Optional
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from logic import DatabaseManager
from app.repo.abstract_repository import AbstractRepository
from app.repo.sqlite_repository import SQLiteRepository


class RepositoryFactory:
    """
    Factory for creating repository instances.
    
    Supports creating SQLite and Firestore repositories based on configuration.
    """
    
    @staticmethod
    def create_sqlite_repository(db_path: str = "progain_database.db") -> AbstractRepository:
        """
        Create a SQLite repository.
        
        Args:
            db_path: Path to the SQLite database file
            
        Returns:
            A SQLiteRepository instance
        """
        db_manager = DatabaseManager(db_path)
        return SQLiteRepository(db_manager)
    
    @staticmethod
    def create_repository_from_db_manager(db_manager: DatabaseManager) -> AbstractRepository:
        """
        Create a repository from an existing DatabaseManager instance.
        
        This is useful for backward compatibility with existing code that
        already has a DatabaseManager instance.
        
        Args:
            db_manager: Existing DatabaseManager instance
            
        Returns:
            A SQLiteRepository wrapping the DatabaseManager
        """
        return SQLiteRepository(db_manager)
    
    @staticmethod
    def create_firestore_repository(
        credentials_path: Optional[str] = None,
        project_id: Optional[str] = None
    ) -> AbstractRepository:
        """
        Create a Firestore repository.
        
        Args:
            credentials_path: Path to Firebase service account JSON file
            project_id: Firebase project ID
            
        Returns:
            A FirestoreRepository instance
            
        Raises:
            NotImplementedError: Firestore repository not yet implemented
        """
        raise NotImplementedError(
            "Firestore repository will be implemented in a future PR. "
            "Currently only SQLite is supported."
        )
    
    @staticmethod
    def create_default_repository(config: Optional[dict] = None) -> AbstractRepository:
        """
        Create a repository based on configuration.
        
        Args:
            config: Configuration dictionary with database settings.
                   Expected keys:
                   - 'backend': 'sqlite' or 'firestore' (default: 'sqlite')
                   - 'database_path': Path to SQLite database (for SQLite backend)
                   - 'credentials_path': Path to Firebase credentials (for Firestore)
                   - 'project_id': Firebase project ID (for Firestore)
        
        Returns:
            An AbstractRepository instance (SQLite or Firestore)
        """
        config = config or {}
        backend = config.get('backend', 'sqlite')
        
        if backend == 'sqlite':
            db_path = config.get('database_path', 'progain_database.db')
            return RepositoryFactory.create_sqlite_repository(db_path)
        elif backend == 'firestore':
            credentials_path = config.get('credentials_path')
            project_id = config.get('project_id')
            return RepositoryFactory.create_firestore_repository(credentials_path, project_id)
        else:
            raise ValueError(f"Unknown repository backend: {backend}")
