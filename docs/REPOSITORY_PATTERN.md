# Repository Pattern Documentation

## Overview

The repository abstraction layer provides a clean separation between the application's business logic and data persistence. This allows the application to work with different backends (SQLite, Firestore) without changing the UI or business logic code.

## Architecture

```
┌─────────────────┐
│   UI Layer      │  (app_gui_qt.py, dialogo_*.py, etc.)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│   Repository    │  (AbstractRepository interface)
└────────┬────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌─────────┐ ┌──────────┐
│ SQLite  │ │Firestore │  (Implementations)
│  Repo   │ │   Repo   │
└─────────┘ └──────────┘
```

## Components

### 1. AbstractRepository (`app/repo/abstract_repository.py`)

Defines the contract that all repository implementations must follow. Includes methods for:

- **Projects**: CRUD operations for projects
- **Equipment**: Managing equipment records
- **Entities**: Managing clients and operators
- **Rentals/Transactions**: Rental operations
- **Maintenance**: Equipment maintenance records
- **Payments**: Payment and abono tracking
- **Dashboard/KPIs**: Analytics and reporting data
- **Accounts/Categories**: Chart of accounts

### 2. SQLiteRepository (`app/repo/sqlite_repository.py`)

Wraps the existing `DatabaseManager` (from `logic.py`) to implement the `AbstractRepository` interface. This provides:

- Backward compatibility with existing code
- A consistent interface for future backends
- Easy testing and mocking

### 3. RepositoryFactory (`app/repo/repository_factory.py`)

Factory class for creating repository instances. Provides methods:

- `create_sqlite_repository(db_path)`: Create SQLite repo
- `create_repository_from_db_manager(db_manager)`: Wrap existing DatabaseManager
- `create_firestore_repository(...)`: Future Firestore support
- `create_default_repository(config)`: Create based on config

## Usage

### Basic Usage (New Code)

```python
from app.repo.repository_factory import RepositoryFactory

# Create repository
repo = RepositoryFactory.create_sqlite_repository("my_database.db")

# Use repository
proyectos = repo.obtener_proyectos()
equipos = repo.obtener_equipos(proyecto_id=1)
```

### Backward Compatibility (Existing Code)

```python
from logic import DatabaseManager
from app.repo.repository_factory import RepositoryFactory

# Existing code has DatabaseManager
db_manager = DatabaseManager("progain_database.db")

# Wrap it in a repository
repo = RepositoryFactory.create_repository_from_db_manager(db_manager)

# Now can use repository interface
# But also direct access when needed
db_manager = repo.get_db_manager()
```

### Configuration-Based Creation

```python
from app.repo.repository_factory import RepositoryFactory

config = {
    'backend': 'sqlite',  # or 'firestore' in the future
    'database_path': 'progain_database.db'
}

repo = RepositoryFactory.create_default_repository(config)
```

## Migration Strategy

The repository pattern is introduced with **minimal changes** to existing code:

### Phase 1: Repository Layer (Current)
- ✅ Create abstract repository interface
- ✅ Implement SQLite repository (wraps existing DatabaseManager)
- ✅ Create factory for easy instantiation
- ✅ Tests to verify functionality

### Phase 2: Gradual Adoption (Future PRs)
- Inject repository into UI components
- Replace direct DatabaseManager calls with repository calls
- Maintain backward compatibility via `get_db_manager()`

### Phase 3: Firestore Support (Future PRs)
- Implement `FirestoreRepository`
- Add configuration to choose backend
- Implement migration tools

## Testing

Run repository tests:

```bash
python test_repository.py
```

The test suite verifies:
1. Repository creation from DatabaseManager
2. Factory methods work correctly
3. Basic CRUD operations
4. Integration with existing database

## Benefits

1. **Flexibility**: Easy to switch between SQLite and Firestore
2. **Testability**: Can mock repositories for unit tests
3. **Maintainability**: Clear separation of concerns
4. **Backward Compatibility**: Existing code continues to work
5. **Future-Proof**: Ready for Firebase migration

## Next Steps

1. **PR2**: Fix alquiler edit duplication issue
2. **PR3**: Complete entities management with new methods
3. **PR4-5**: Firebase migration UI and implementation
4. **PR6+**: UI modernization with themes and shortcuts

## API Reference

See `app/repo/abstract_repository.py` for the complete interface documentation.
