"""
Configuración para el proceso de migración.
"""
import os

# Tamaño de batch para operaciones de Firestore (máximo 500)
BATCH_SIZE = 500

# Archivos de control
CHECKPOINT_FILE = "migration_checkpoint.json"
LOG_FILE = "migration.log"
MAPPING_FILE = "mapping.json"
SUMMARY_FILE = "migration_summary.json"

# Rutas de Cloud Storage
STORAGE_BASE_PATH = "projects"
CONDUCES_PATH = "conduces"

# Configuración de reintentos
MAX_RETRIES = 3
RETRY_DELAY = 1  # segundos

# Tablas a migrar (en orden de dependencias)
MIGRATION_ORDER = [
    'proyectos',
    'cuentas',
    'categorias',
    'subcategorias',
    'equipos',
    'equipos_entidades',
    'transacciones',
    'equipos_alquiler_meta',
    'pagos',
    'mantenimientos'
]

# Mapeo de columnas especiales que requieren transformación
DATE_COLUMNS = ['fecha', 'created_at', 'updated_at', 'migrated_at']
ATTACHMENT_COLUMNS = ['conduce_adjunto_path']
