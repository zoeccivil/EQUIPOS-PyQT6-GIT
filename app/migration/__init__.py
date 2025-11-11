"""
Migration Package

Handles migration of data from SQLite to Firebase Firestore and Cloud Storage.

Arquitectura modular:
- FirebaseMigrator: Coordinador principal de migración
- IDMapper: Gestiona mapeo de IDs SQLite -> Firestore
- FirebaseAuth: Autenticación con Firebase
- SQLiteReader: Lectura de datos de SQLite
- FirestoreWriter: Escritura a Firestore
- config: Configuración centralizada
"""
from app.migration.firebase_migrator import FirebaseMigrator, MigrationError
from app.migration.id_mapper import IDMapper
from app.migration.firebase_auth import FirebaseAuth, FirebaseAuthError
from app.migration.sqlite_reader import SQLiteReader, SQLiteReaderError
from app.migration.firestore_writer import FirestoreWriter, FirestoreWriteError

__all__ = [
    'FirebaseMigrator',
    'MigrationError',
    'IDMapper',
    'FirebaseAuth',
    'FirebaseAuthError',
    'SQLiteReader',
    'SQLiteReaderError',
    'FirestoreWriter',
    'FirestoreWriteError',
]
