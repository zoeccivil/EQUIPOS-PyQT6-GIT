"""
Repository pattern implementation for EQUIPOS PyQt6.
Provides abstraction layer for data persistence, enabling switching between SQLite and Firebase.
"""

from .base_repo import BaseRepository
from .sqlite_repo import SQLiteRepository

__all__ = ['BaseRepository', 'SQLiteRepository']
