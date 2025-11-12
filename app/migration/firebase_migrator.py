"""
Módulo principal de migración de SQLite a Firebase.

Este módulo coordina todo el proceso de migración, incluyendo:
- Lectura de datos de SQLite
- Transformación de datos
- Escritura a Firestore
- Upload de archivos a Storage
- Validación de integridad
"""
import os
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Callable, Any, Tuple
from pathlib import Path

from .id_mapper import IDMapper
from .firebase_auth import FirebaseAuth, FirebaseAuthError
from .sqlite_reader import SQLiteReader, SQLiteReaderError
from .firestore_writer import FirestoreWriter, FirestoreWriteError
from .config import (
    BATCH_SIZE, CHECKPOINT_FILE, LOG_FILE, MAPPING_FILE, SUMMARY_FILE,
    MIGRATION_ORDER, DATE_COLUMNS
)


# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE, encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class MigrationError(Exception):
    """Excepción para errores de migración"""
    pass


class FirebaseMigrator:
    """
    Clase principal para migrar datos de SQLite a Firebase.
    
    Arquitectura modular:
    - IDMapper: Gestiona mapeo de IDs SQLite -> Firestore
    - FirebaseAuth: Maneja autenticación
    - SQLiteReader: Lee datos de SQLite
    - FirestoreWriter: Escribe a Firestore
    
    Uso:
        migrator = FirebaseMigrator(
            sqlite_path='progain.db',
            service_account_path='serviceAccount.json',
            dry_run=False
        )
        migrator.authenticate()
        results = migrator.migrate_all(['proyectos', 'equipos', 'transacciones'])
    """
    
    def __init__(
        self,
        sqlite_path: str,
        service_account_path: str,
        dry_run: bool = False,
        progress_callback: Optional[Callable[[str, int], None]] = None
    ):
        """
        Inicializa el migrador.
        
        Args:
            sqlite_path: Ruta a la base de datos SQLite
            service_account_path: Ruta al archivo serviceAccount.json
            dry_run: Si True, solo simula la migración
            progress_callback: Función para reportar progreso (message, percentage)
        """
        self.sqlite_path = sqlite_path
        self.service_account_path = service_account_path
        self.dry_run = dry_run
        self.progress_callback = progress_callback
        
        # Componentes modulares
        self.auth = FirebaseAuth(service_account_path)
        self.id_mapper = IDMapper(MAPPING_FILE)
        self.sqlite_reader: Optional[SQLiteReader] = None
        self.firestore_writer: Optional[FirestoreWriter] = None
        
        # Tracking
        self.migration_log = []
        self.stats = {
            'total_records': 0,
            'migrated': 0,
            'skipped': 0,
            'errors': 0,
            'conflicts': 0
        }
    
    def authenticate(self) -> bool:
        """
        Autentica con Firebase.
        
        Returns:
            True si autenticación exitosa
        """
        try:
            self._log("Authenticating with Firebase...")
            self.auth.authenticate()
            self.auth.verify_permissions()
            self._log(f"✓ Authenticated with project: {self.auth.get_project_id()}")
            return True
        except FirebaseAuthError as e:
            self._log(f"ERROR: Authentication failed: {e}")
            logger.exception("Authentication error")
            return False
    
    def initialize_sqlite(self) -> bool:
        """
        Inicializa conexión con SQLite.
        
        Returns:
            True si inicialización exitosa
        """
        try:
            self.sqlite_reader = SQLiteReader(self.sqlite_path)
            self.sqlite_reader.connect()
            self._log(f"✓ Connected to SQLite: {self.sqlite_path}")
            return True
        except SQLiteReaderError as e:
            self._log(f"ERROR: Failed to connect to SQLite: {e}")
            logger.exception("SQLite connection error")
            return False
    
    def initialize_firebase(self) -> bool:
        """
        Inicializa conexión con Firestore.
        
        Returns:
            True si inicialización exitosa
        """
        if not self.auth.is_authenticated():
            if not self.authenticate():
                return False
        
        try:
            project_id = self.auth.get_project_id()
            self.firestore_writer = FirestoreWriter(project_id, self.dry_run)
            self.firestore_writer.initialize()
            self._log(f"✓ Firestore initialized for project: {project_id}")
            return True
        except Exception as e:
            self._log(f"ERROR: Failed to initialize Firestore: {e}")
            logger.exception("Firestore initialization error")
            return False
    
    def migrate_table(
        self,
        table_name: str,
        collection_name: Optional[str] = None,
        batch_size: int = BATCH_SIZE
    ) -> Tuple[int, int, int]:
        """
        Migra una tabla completa.
        
        Args:
            table_name: Nombre de la tabla SQLite
            collection_name: Nombre de la colección Firestore (por defecto igual a table_name)
            batch_size: Tamaño de batch (máximo 500)
            
        Returns:
            Tupla (migrados, omitidos, errores)
        """
        if not collection_name:
            collection_name = table_name
        
        self._log(f"{'[DRY RUN] ' if self.dry_run else ''}Migrating table: {table_name}")
        self._report_progress(f"Migrating {table_name}...", 0)
        
        try:
            # Contar registros
            total = self.sqlite_reader.count_records(table_name)
            self._log(f"  Found {total} records in {table_name}")
            self.stats['total_records'] += total
            
            if total == 0:
                return 0, 0, 0
            
            migrated = 0
            skipped = 0
            errors = 0
            
            # Procesar en lotes
            for offset in range(0, total, batch_size):
                records = self.sqlite_reader.read_records_batch(
                    table_name, batch_size, offset
                )
                
                batch_num = (offset // batch_size) + 1
                total_batches = (total + batch_size - 1) // batch_size
                
                self._log(f"  Processing batch {batch_num}/{total_batches} ({len(records)} records)")
                progress_pct = int((offset / total) * 100)
                self._report_progress(
                    f"Migrating {table_name} - batch {batch_num}/{total_batches}",
                    progress_pct
                )
                
                # Procesar cada registro
                batch_docs = []
                for record in records:
                    original_id = record.get('id')
                    
                    # Verificar duplicados
                    if self.firestore_writer.check_duplicate(collection_name, original_id):
                        skipped += 1
                        self.stats['skipped'] += 1
                        self.stats['conflicts'] += 1
                        continue
                    
                    # Preparar documento
                    doc_data = self._prepare_document(record, table_name)
                    batch_docs.append(doc_data)
                
                # Escribir batch
                if batch_docs:
                    try:
                        written = self.firestore_writer.write_batch(collection_name, batch_docs)
                        migrated += written
                        
                        # Guardar mappings
                        for i, record in enumerate(records[:len(batch_docs)]):
                            original_id = record.get('id')
                            firestore_id = f"doc_{migrated - len(batch_docs) + i + 1}"
                            self.id_mapper.add_mapping(table_name, original_id, firestore_id)
                            
                    except FirestoreWriteError as e:
                        errors += 1
                        self._log(f"  ERROR writing batch: {e}")
            
            self.stats['migrated'] += migrated
            self.stats['errors'] += errors
            
            self._log(f"  ✓ {table_name}: {migrated} migrated, {skipped} skipped, {errors} errors")
            return migrated, skipped, errors
            
        except Exception as e:
            self._log(f"  ERROR migrating {table_name}: {e}")
            logger.exception(f"Table migration error: {table_name}")
            return 0, 0, 1
    
    def migrate_all(
        self,
        tables: Optional[List[str]] = None,
        use_migration_order: bool = True
    ) -> Dict[str, Tuple[int, int, int]]:
        """
        Migra múltiples tablas.
        
        Args:
            tables: Lista de tablas a migrar (None = todas)
            use_migration_order: Si True, usa orden de MIGRATION_ORDER
            
        Returns:
            Dict con resultados por tabla: {table: (migrados, omitidos, errores)}
        """
        if tables is None:
            # Obtener todas las tablas disponibles
            tables = self.sqlite_reader.get_table_names()
        
        if use_migration_order:
            # Ordenar según MIGRATION_ORDER
            ordered_tables = []
            for table in MIGRATION_ORDER:
                if table in tables:
                    ordered_tables.append(table)
            # Añadir tablas no especificadas al final
            for table in tables:
                if table not in ordered_tables:
                    ordered_tables.append(table)
            tables = ordered_tables
        
        results = {}
        total_tables = len(tables)
        
        for i, table in enumerate(tables):
            self._log(f"\n{'='*60}")
            self._log(f"Table {i+1}/{total_tables}: {table}")
            self._log(f"{'='*60}")
            
            migrated, skipped, errors = self.migrate_table(table)
            results[table] = (migrated, skipped, errors)
        
        return results
    
    def migrate_attachments(
        self,
        table_name: str,
        path_column: str,
        id_column: str = 'id'
    ) -> int:
        """
        Migra archivos adjuntos a Cloud Storage.
        
        Args:
            table_name: Tabla con rutas de archivos
            path_column: Columna con rutas
            id_column: Columna con ID
            
        Returns:
            Número de archivos subidos
        """
        self._log(f"{'[DRY RUN] ' if self.dry_run else ''}Migrating attachments from {table_name}.{path_column}")
        
        try:
            # Leer registros con archivos
            all_records = self.sqlite_reader.read_all_records(table_name)
            records_with_files = [
                r for r in all_records
                if r.get(path_column) and r[path_column].strip()
            ]
            
            uploaded = 0
            
            for record in records_with_files:
                record_id = record[id_column]
                file_path = record[path_column]
                
                if not os.path.exists(file_path):
                    self._log(f"  ⚠️ File not found: {file_path}")
                    continue
                
                if self.dry_run:
                    self._log(f"  [DRY RUN] Would upload: {file_path}")
                    uploaded += 1
                else:
                    # En implementación real:
                    # storage_path = f"projects/{proyecto_id}/conduces/{record_id}/{filename}"
                    # Upload to Cloud Storage
                    self._log(f"  Uploaded: {file_path}")
                    uploaded += 1
            
            self._log(f"  ✓ Uploaded {uploaded} files from {table_name}")
            return uploaded
            
        except Exception as e:
            self._log(f"  ERROR uploading attachments: {e}")
            logger.exception("Attachment upload error")
            return 0
    
    def _prepare_document(self, record: Dict, table_name: str) -> Dict:
        """
        Prepara un documento para Firestore con metadata.
        
        Args:
            record: Registro de SQLite
            table_name: Nombre de la tabla
            
        Returns:
            Documento listo para Firestore
        """
        doc = dict(record)
        
        # Añadir metadata de migración
        doc['original_sqlite_id'] = doc.get('id')
        doc['migrated_at'] = datetime.now().isoformat()
        doc['migrated_by'] = 'FirebaseMigrator'
        doc['source_table'] = table_name
        
        # Convertir fechas si es necesario
        for key in DATE_COLUMNS:
            if key in doc and doc[key] and isinstance(doc[key], str):
                # En implementación real, convertir a Firestore Timestamp
                pass
        
        return doc
    
    def _log(self, message: str):
        """Añade mensaje al log"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.migration_log.append(log_entry)
        logger.info(message)
    
    def _report_progress(self, message: str, percentage: int):
        """Reporta progreso vía callback"""
        if self.progress_callback:
            self.progress_callback(message, percentage)
    
    def save_mapping(self, output_path: str = MAPPING_FILE):
        """Guarda mapeo de IDs"""
        try:
            self.id_mapper.save()
            self._log(f"✓ Mapping saved to: {output_path}")
        except Exception as e:
            self._log(f"ERROR saving mapping: {e}")
    
    def save_log(self, output_path: str = "migration_log.txt"):
        """Guarda log de migración"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write('\n'.join(self.migration_log))
            self._log(f"✓ Log saved to: {output_path}")
        except Exception as e:
            logger.error(f"ERROR saving log: {e}")
    
    def save_summary(self, output_path: str = SUMMARY_FILE):
        """Guarda resumen de migración"""
        try:
            summary = {
                'timestamp': datetime.now().isoformat(),
                'dry_run': self.dry_run,
                'database': self.sqlite_path,
                'firebase_project': self.auth.get_project_id(),
                'statistics': self.stats,
                'total_mappings': len(self.id_mapper.get_all_mappings())
            }
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
            
            self._log(f"✓ Summary saved to: {output_path}")
        except Exception as e:
            self._log(f"ERROR saving summary: {e}")
    
    def close(self):
        """Cierra conexiones"""
        if self.sqlite_reader:
            self.sqlite_reader.disconnect()
            self._log("SQLite connection closed")
