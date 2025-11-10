"""
Repository Package

Provides data access abstraction layer for PROGAIN application.
Supports multiple backends (SQLite, Firestore) through a common interface.
"""
from app.repo.abstract_repository import AbstractRepository
from app.repo.sqlite_repository import SQLiteRepository
from app.repo.repository_factory import RepositoryFactory

__all__ = [
    'AbstractRepository',
    'SQLiteRepository',
    'RepositoryFactory',
]
