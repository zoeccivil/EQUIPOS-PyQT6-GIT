# Arquitectura del Sistema - Diagrama Visual

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         FIRESTORE (Cloud)                               │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌──────────────┐  │
│  │  Proyectos  │  │   Equipos   │  │  Clientes   │  │  Operadores  │  │
│  └─────────────┘  └─────────────┘  └─────────────┘  └──────────────┘  │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌──────────────┐  │
│  │ Alquileres  │  │Transacciones│  │    Pagos    │  │Mantenimientos│  │
│  └─────────────┘  └─────────────┘  └─────────────┘  └──────────────┘  │
└────────────────────────────────┬────────────────────────────────────────┘
                                 │
                                 │ HTTPS / REST API
                                 │ (Authentication: Email/Password)
                                 │
        ┌────────────────────────▼────────────────────────┐
        │      FirestoreRepository                        │
        │  - Autenticación con email/password             │
        │  - CRUD operations via REST API                 │
        │  - Conversión de formatos Firestore             │
        └────────────────────────┬────────────────────────┘
                                 │
                                 │ implements
                                 │
        ┌────────────────────────▼────────────────────────┐
        │         BaseRepository (Interface)              │
        │  - obtener_proyectos()                          │
        │  - obtener_equipos()                            │
        │  - crear_alquiler()                             │
        │  - ... (métodos abstractos)                     │
        └────────────────────────┬────────────────────────┘
                                 │
                ┌────────────────┴────────────────┐
                │                                 │
                │                                 │ implements
                │                                 │
┌───────────────▼──────────────┐   ┌─────────────▼────────────────┐
│   FirestoreRepository        │   │   SQLiteRepository           │
│   (Producción)               │   │   (Migration/Backup)         │
└───────────────┬──────────────┘   └─────────────┬────────────────┘
                │                                 │
                │                                 │ wraps
                │                                 │
                │                  ┌──────────────▼────────────────┐
                │                  │   DatabaseManager (Legacy)    │
                │                  │   - Código SQLite existente   │
                │                  └──────────────┬────────────────┘
                │                                 │
                │                                 │
                └──────────────┬──────────────────┘
                               │
                               │ created by
                               │
                ┌──────────────▼────────────────────┐
                │     RepositoryFactory             │
                │  - create_from_settings()         │
                │  - create_firestore()             │
                │  - create_sqlite()                │
                └──────────────┬────────────────────┘
                               │
                               │ uses
                               │
                ┌──────────────▼────────────────────┐
                │        AppSettings                │
                │  - get_data_source()              │
                │  - get_firestore_config()         │
                │  - is_firestore_configured()      │
                └──────────────┬────────────────────┘
                               │
                               │ read by
                               │
        ┌──────────────────────▼───────────────────────────┐
        │              main_qt.py                          │
        │  1. Carga AppSettings                            │
        │  2. Determina data_source (firestore/sqlite)     │
        │  3. Crea Repository via Factory                  │
        │  4. Pasa repository a AppGUI                     │
        └──────────────────────┬───────────────────────────┘
                               │
                               │ initializes
                               │
        ┌──────────────────────▼───────────────────────────┐
        │              AppGUI                              │
        │  - Tabs (Registro, Gastos, Pagos, Dashboard)    │
        │  - Menú Herramientas (Migration/Backup)         │
        │  - Menú Configuración (Data Source)             │
        └──────────────────────┬───────────────────────────┘
                               │
                               │ opens
                               │
        ┌──────────────────────┴───────────────────────────┐
        │                                                   │
        ▼                      ▼                           ▼
┌───────────────┐  ┌─────────────────────┐  ┌──────────────────────┐
│DataSourceWidget│  │DialogoMigracion    │  │DialogoBackupSQLite   │
│                │  │Firestore            │  │                      │
│- Config UI     │  │                     │  │                      │
│- Test conexión │  │SQLite → Firestore   │  │Firestore → SQLite    │
│- Guardar       │  │                     │  │                      │
└────────────────┘  └─────────────────────┘  └──────────────────────┘


═══════════════════════════════════════════════════════════════════════

FLUJO DE DATOS

┌─────────────┐
│   Usuario   │
└──────┬──────┘
       │
       │ 1. Inicia app
       ▼
┌─────────────┐     ┌──────────────────┐
│  main_qt.py │────▶│   AppSettings    │
└──────┬──────┘     └──────────────────┘
       │                     │
       │ 2. Decide fuente    │
       │    de datos         │
       │◀────────────────────┘
       │
       │ 3. Si Firestore
       ▼
┌──────────────────┐
│RepositoryFactory │
└────────┬─────────┘
         │
         │ 4. Crea
         ▼
┌───────────────────┐
│FirestoreRepository│─────┐
└───────────────────┘     │
                          │ 5. Autentica
                          ▼
                 ┌─────────────────┐
                 │ Firebase Auth   │
                 │ (email/password)│
                 └────────┬────────┘
                          │
                          │ 6. Token JWT
                          ▼
                 ┌─────────────────┐
                 │   Firestore     │
                 │   REST API      │
                 └────────┬────────┘
                          │
                          │ 7. Datos
                          ▼
┌───────────────────┐
│   AppGUI          │
│   - Tabs          │
│   - UI            │
└───────────────────┘

═══════════════════════════════════════════════════════════════════════

MIGRACIÓN: SQLite → Firestore

┌──────────────────┐
│  SQLite DB       │
│  (Datos Legacy)  │
└────────┬─────────┘
         │
         │ 1. Usuario selecciona
         ▼
┌──────────────────┐
│ Migration Dialog │
└────────┬─────────┘
         │
         │ 2. Crea repos
         ▼
┌─────────────────────────────────┐
│  SQLiteRepository (source)      │
│  FirestoreRepository (target)   │
└────────┬────────────────────────┘
         │
         │ 3. Lee datos
         │    - Proyectos
         │    - Equipos
         │    - Clientes
         │    - Alquileres
         │    - etc.
         ▼
┌──────────────────┐
│  MigrationWorker │
│  (QThread)       │
└────────┬─────────┘
         │
         │ 4. Escribe a Firestore
         │    (evita duplicados por ID)
         ▼
┌──────────────────┐
│    Firestore     │
│  (Datos nuevos)  │
└──────────────────┘

═══════════════════════════════════════════════════════════════════════

BACKUP: Firestore → SQLite

┌──────────────────┐
│    Firestore     │
│  (Datos Cloud)   │
└────────┬─────────┘
         │
         │ 1. Usuario solicita backup
         ▼
┌──────────────────┐
│  Backup Dialog   │
└────────┬─────────┘
         │
         │ 2. Crea repos
         ▼
┌─────────────────────────────────┐
│  FirestoreRepository (source)   │
│  SQLiteRepository (target)      │
└────────┬────────────────────────┘
         │
         │ 3. Lee todos los datos
         ▼
┌──────────────────┐
│  BackupWorker    │
│  (QThread)       │
└────────┬─────────┘
         │
         │ 4. Escribe a SQLite
         │    (crea tablas si no existen)
         ▼
┌──────────────────────────────────┐
│  backup_firestore_TIMESTAMP.db   │
│  (Snapshot local)                │
└──────────────────────────────────┘

═══════════════════════════════════════════════════════════════════════

CONFIGURACIÓN

app_settings.json (Local, gitignored)
┌────────────────────────────────────────┐
│ {                                      │
│   "data_source": "firestore",          │
│   "firestore": {                       │
│     "project_id": "mi-proyecto",       │
│     "api_key": "AIza...",              │
│     "email": "admin@empresa.com",      │
│     "password": "******"               │
│   },                                   │
│   "backup": {                          │
│     "sqlite_folder": "./backups"       │
│   }                                    │
│ }                                      │
└────────────────────────────────────────┘

═══════════════════════════════════════════════════════════════════════

ARCHIVOS CLAVE

Configuración:
  app_settings.json          # Credenciales y configuración
  equipos_config.json        # Config legacy (carpeta_conduces)

Arquitectura Core:
  app/app_settings.py        # Gestión de configuración
  app/repo/base_repository.py          # Interface
  app/repo/firestore_repository.py     # Implementación Firestore
  app/repo/sqlite_repository.py        # Implementación SQLite
  app/repo/repository_factory.py       # Factory

UI:
  app/ui/data_source_widget.py         # Config dialog
  app/ui/migration_dialog.py           # Migration UI
  app/ui/backup_dialog.py              # Backup UI

Main:
  main_qt.py                 # Startup con nueva arquitectura
  app_gui_qt.py              # GUI principal + nuevos menús

Documentación:
  README.md                  # Overview del proyecto
  FIRESTORE_SETUP.md         # Guía de configuración
  IMPLEMENTATION_SUMMARY.md  # Detalles técnicos

═══════════════════════════════════════════════════════════════════════
```
