# Data Source Integration Guide

## Overview

The PROGAIN equipment rental system now supports dual data backends:
- **SQLite** (local database)
- **Firebase Firestore** (cloud database)

Users can seamlessly switch between backends via the UI without code changes.

## Features

### 1. Visual Data Source Indicator

The main window's status bar shows which data source is currently active:

- **🗄️ SQLite: progain_database.db** (Blue background)
- **☁️ Firestore: progain-prod** (Orange background)

### 2. Configuration Dialog

Access via: **Menu → Configuración → Fuente de Datos (SQLite/Firestore)**

The dialog allows users to:
- Select data source (radio buttons)
- Configure SQLite database path
- Configure Firestore credentials (service account + project ID)
- Apply changes and restart the application

### 3. Persistent Settings

Configuration is saved to `app_settings.json` and persists across sessions.

Settings include:
- `data_source`: 'sqlite' or 'firestore'
- `sqlite.db_path`: Path to SQLite database
- `firestore.service_account`: Path to Firebase credentials
- `firestore.project_id`: Firebase project ID

## Usage

### Switching from SQLite to Firestore

1. Open the application
2. Go to **Configuración → Fuente de Datos (SQLite/Firestore)**
3. Select **Firebase Firestore**
4. Click **Explorar** to select your `serviceAccount.json` file
5. Enter your Firebase **Project ID** (e.g., "progain-prod")
6. Click **Aplicar y Reiniciar**
7. Confirm the restart prompt
8. Application will relaunch using Firestore

### Switching from Firestore to SQLite

1. Open the application
2. Go to **Configuración → Fuente de Datos (SQLite/Firestore)**
3. Select **SQLite (Base de datos local)**
4. Click **Explorar** to select your `.db` file
5. Click **Aplicar y Reiniciar**
6. Confirm the restart prompt
7. Application will relaunch using SQLite

## Architecture

### Repository Pattern

The application uses the repository pattern to abstract data access:

```python
# Abstract interface
AbstractRepository
├── obtener_proyectos()
├── obtener_equipos()
├── guardar_alquiler()
└── ... 30+ methods

# Implementations
SQLiteRepository (wraps DatabaseManager)
FirestoreRepository (uses Firebase Admin SDK)
```

### Initialization Flow

```
main_qt.py
    ↓
1. Load AppSettings
    ↓
2. Check data_source
    ↓
3. Create appropriate repository
    ├─→ SQLite: Create DatabaseManager
    └─→ Firestore: Create FirestoreRepository
    ↓
4. Pass to AppGUI
    ↓
5. Display indicator in status bar
```

### Key Files

```
app/
├── app_settings.py              # Configuration management
├── repo/
│   ├── abstract_repository.py   # Interface
│   ├── sqlite_repository.py     # SQLite implementation
│   ├── firestore_repository.py  # Firestore implementation
│   └── repository_factory.py    # Creates repositories
└── ui/
    └── data_source_widget.py    # Configuration dialog

app_gui_qt.py                    # Main window with status bar
main_qt.py                       # Entry point with data source logic
```

## Developer Guide

### Adding Support for a New Backend

1. Create a new repository class implementing `AbstractRepository`:
   ```python
   from app.repo.abstract_repository import AbstractRepository
   
   class MongoDBRepository(AbstractRepository):
       def obtener_proyectos(self):
           # Implementation
           pass
   ```

2. Add factory method in `repository_factory.py`:
   ```python
   @staticmethod
   def create_mongodb_repository(connection_string):
       return MongoDBRepository(connection_string)
   ```

3. Update `DataSourceWidget` to include MongoDB option

4. Update `app_settings.py` with MongoDB configuration keys

### Using the Repository in Code

```python
# From settings (automatic backend selection)
from app.app_settings import get_app_settings
from app.repo.repository_factory import RepositoryFactory

settings = get_app_settings()
repo = RepositoryFactory.create_from_settings(settings)

# Use repository methods
proyectos = repo.obtener_proyectos()
equipos = repo.obtener_equipos(proyecto_id=1)

# Direct SQLite
repo = RepositoryFactory.create_sqlite_repository("progain.db")

# Direct Firestore
repo = RepositoryFactory.create_firestore_repository(
    "serviceAccount.json",
    "progain-prod"
)
```

### Backward Compatibility

For code that still uses `DatabaseManager` directly:

```python
# SQLiteRepository provides get_db_manager()
repo = RepositoryFactory.create_sqlite_repository("progain.db")
db = repo.get_db_manager()  # Returns DatabaseManager instance

# Now you can use the old API
db.obtener_proyectos()
```

## Testing

Run integration tests:
```bash
python test_data_source_integration.py
```

Tests verify:
- Menu integration
- Status bar indicator
- main_qt.py data source logic
- Required modules present
- Settings persistence

## Troubleshooting

### "No se pudo conectar a Firestore"

**Cause**: Invalid or missing Firebase credentials

**Solution**:
1. Ensure `serviceAccount.json` exists and is valid
2. Verify project ID matches your Firebase project
3. Check internet connection
4. Verify Firebase Admin SDK is installed: `pip install firebase-admin`

### Application Falls Back to SQLite

**Expected Behavior**: If Firestore connection fails, the app automatically falls back to SQLite to prevent data loss.

**To Fix**:
1. Check error message in logs (`progain.log`)
2. Verify Firestore configuration
3. Try reconnecting via the configuration dialog

### Status Bar Shows Wrong Data Source

**Solution**: Restart the application. Settings are loaded at startup.

### Configuration Changes Don't Apply

**Solution**:
1. Ensure you clicked "Aplicar y Reiniciar"
2. Confirm restart when prompted
3. Check `app_settings.json` was updated

## Security

### Credentials Management

⚠️ **IMPORTANT**: Never commit credentials to git!

- `serviceAccount.json` is in `.gitignore`
- `app_settings.json` is in `.gitignore`
- Only file paths are stored, not credentials

### Best Practices

1. Store `serviceAccount.json` outside the repository
2. Use environment variables for sensitive data in production
3. Rotate Firebase credentials periodically
4. Use Firebase security rules to restrict access

## Future Enhancements

Planned improvements:
- [ ] Hybrid mode (local cache + cloud sync)
- [ ] Automatic conflict resolution
- [ ] Offline mode with sync queue
- [ ] Multi-user collaboration features
- [ ] Real-time updates via Firestore listeners
- [ ] Migration progress tracking in UI
- [ ] Rollback capability
- [ ] Data validation on backend switch

## Related Documentation

- [FIREBASE_MIGRATION_GUIDE.md](FIREBASE_MIGRATION_GUIDE.md) - How to migrate data
- [FIREBASE_MIGRATOR.md](FIREBASE_MIGRATOR.md) - Migration architecture
- [REPOSITORY_PATTERN.md](REPOSITORY_PATTERN.md) - Repository pattern details

## Support

For issues or questions:
1. Check logs in `progain.log`
2. Review error messages in UI dialogs
3. Verify configuration in `app_settings.json`
4. Run integration tests to verify installation
