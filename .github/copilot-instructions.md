# AI Agent Instructions: EQUIPOS-PyQT6-GIT

## Project Overview
PyQt6 desktop application for managing heavy equipment rentals. Core business logic: track equipment alquileres (rentals), cliente (client) payments, operador (operator) wages, and equipment gastos (expenses). Recently migrated from SQLite-first to **Firestore-first architecture** with SQLite as backup/migration tool.

## Critical Architecture: Dual Data Sources

### Repository Pattern (app/repo/)
All data access goes through `BaseRepository` interface with two implementations:

**FirestoreRepository** (PRIMARY for production):
- Uses Firebase REST API with email/password auth (NO service account JSON)
- Authentication: `_authenticate()` gets JWT token via `FIREBASE_AUTH_URL`
- See `app/repo/firestore_repository.py` for Firestore-specific conversions
- Requires: `project_id`, `email`, `password`, `api_key` from `app_settings.json`

**SQLiteRepository** (backup/migration only):
- Wraps legacy `DatabaseManager` class from `logic.py`
- Used for: migrating old data to Firestore, creating offline backups
- See `app/repo/sqlite_repository.py`

**Factory Creation Pattern**:
```python
from app.repo.repository_factory import RepositoryFactory
from app.app_settings import get_settings

settings = get_settings()
repo = RepositoryFactory.create_from_settings(settings)  # Returns Firestore or SQLite
```

### Startup Flow (main_qt.py)
1. Load `AppSettings` from `app_settings.json` (git-ignored, contains credentials)
2. Determine `data_source`: "firestore" or "sqlite"
3. Create repository via `RepositoryFactory`
4. Pass repository to `AppGUI` (NOT raw DatabaseManager)
5. If Firestore mode: optionally sync data to temp SQLite for legacy tabs

**NEVER** instantiate `DatabaseManager` directly in new code—use `BaseRepository` interface.

## Key Conventions

### Spanish Domain Language
- All business entities use Spanish: `proyecto`, `equipo`, `cliente`, `operador`, `alquiler`, `transaccion`
- Database tables: `equipos`, `proyectos`, `clientes`, `operadores`, `equipos_alquiler_meta`
- Code comments/logs can be Spanish or English

### Data Models (data_models.py)
Simple dataclasses, not ORMs. Example:
```python
class Proyecto:
    def __init__(self, **kwargs):
        self.id = kwargs.get('id')
        self.nombre = kwargs.get('nombre')
```
Always use `kwargs.get()` for optional fields to handle Firestore/SQLite differences.

### UUID vs Integer IDs
- Legacy SQLite: integer autoincrement IDs
- Firestore: UUID strings (see `uuid_utils.py`)
- Repository methods accept both; handle type conversion in implementation

### Logging Standard
```python
import logging
logger = logging.getLogger(__name__)  # Module-level logger
# All exceptions logged via logger.exception()
# Log file: progain.log (configured in main_qt.py)
```

## PyQt6 UI Patterns

### Tab Architecture (app_gui_qt.py)
Main window uses `QTabWidget` with 4 tabs:
1. `RegistroAlquileresTab` - Main rentals CRUD
2. `TabGastosEquipos` - Equipment expenses
3. `TabPagosOperadores` - Operator payments
4. `DashboardTab` - Analytics/charts

Each tab receives: `db` (legacy DatabaseManager), `proyecto_actual`, `config`, `repository` (new)

### Dialog Pattern
All CRUD dialogs inherit `QDialog`:
- Constructor takes `db`, optional record for editing
- Use `exec()` for modal, check `DialogCode.Accepted`
- Example: `DialogoAlquiler`, `VentanaGestionEntidad`

**Standard error handling**:
```python
try:
    # operation
except Exception as e:
    logger.exception("Context message: %s", e)
    QMessageBox.critical(self, "Error", f"Descripción: {e}")
```

### File Dialogs for "Conduces" (Attachments)
Equipment rental receipts ("conduces") saved via:
```python
from adjuntos import guardar_conduce
path = guardar_conduce(source_path, proyecto_id, config)  # Returns final path
```
Configuration key: `config['carpeta_conduces']` (from `equipos_config.json`)

### Background Tasks (Migration/Backup)
Use `QThread` workers for long operations:
- See `app/ui/migration_dialog.py` → `MigrationWorker(QThread)`
- Emit `pyqtSignal` for progress updates
- Pattern: `worker.finished.connect(self.on_complete)`

## Developer Workflows

### Running Application
```powershell
python main_qt.py
```
No build step required. First run prompts for Firestore credentials if not configured.

### Testing Architecture
```powershell
python test_firestore_architecture.py
```
Tests imports, settings load, repository factory. NO pytest/unittest framework—uses plain `def test_*()` functions.

### Migration: SQLite → Firestore
Via menu: **Herramientas > Migrar desde SQLite a Firestore...**
- Select legacy `.db` file
- Worker reads all tables from SQLite, writes to Firestore
- Skips duplicates by checking existing IDs

### Backup: Firestore → SQLite
Via menu: **Herramientas > Crear Backup SQLite desde Firestore...**
- Creates timestamped `.db` file in backup folder
- Syncs all Firestore collections to SQLite tables

## Configuration Files

### app_settings.json (NOT in git)
```json
{
  "data_source": "firestore",
  "firestore": {
    "project_id": "your-firebase-project",
    "email": "user@example.com",
    "password": "secure-password",
    "api_key": "AIza..."
  }
}
```
**NEVER commit this file.** Use `AppSettings` class to read/write.

### equipos_config.json (legacy, MAY be in git)
```json
{
  "database_path": "progain_database.db",
  "carpeta_conduces": "path/to/receipts"
}
```
Managed by `config_manager.py`. Gradually being replaced by `app_settings.json`.

## Common Gotchas

1. **Mixed Repository Access**: Some tabs still use `self.db` (DatabaseManager). When adding features, prefer `self.repository` (BaseRepository).

2. **Date Handling**: Firestore stores ISO strings, SQLite stores date strings. Use `datetime.fromisoformat()` or check type.

3. **QMessageBox Parent**: Always pass `self` or `None` to avoid crashes:
   ```python
   QMessageBox.warning(self, "Title", "Message")
   ```

4. **Config Dict Keys**: Check both `app_settings.json` and `equipos_config.json` for settings. Use `config.get('key', default)` for safety.

5. **Image Editing**: `MiniEditorImagen` returns PIL Image or QImage. Convert carefully before saving:
   ```python
   # See dialogo_alquiler.py for pattern
   ```

## Reference Files
- Architecture diagram: `ARCHITECTURE_DIAGRAM.md`
- Firestore setup: `FIRESTORE_SETUP.md`
- Repository contract: `app/repo/base_repository.py`
- Main entry point: `main_qt.py` (has startup logic comments)

## When Making Changes

1. **New Data Access**: Implement in both `FirestoreRepository` and `SQLiteRepository`
2. **New Tab/Dialog**: Follow existing tab pattern, accept `repository` parameter
3. **New Config**: Add to `AppSettings` class, not raw JSON
4. **Error Messages**: Log exception details, show user-friendly Spanish message
5. **Database Schema**: Update both Firestore collections and SQLite CREATE TABLE statements
