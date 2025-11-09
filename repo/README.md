# Repository Pattern for EQUIPOS PyQt6

## Overview

This project implements the Repository Pattern to abstract data persistence layer, enabling easy switching between different backends (SQLite, Firebase Firestore).

## Architecture

```
repo/
├── __init__.py           # Package exports
├── base_repo.py          # Abstract base class (interface)
├── sqlite_repo.py        # SQLite implementation
└── firestore_repo.py     # Firebase Firestore implementation (skeleton)
```

## Usage

### Using SQLite Repository (Default)

```python
from repo import SQLiteRepository

# Initialize repository
repo = SQLiteRepository(db_path="progain_database.db")

# Use repository methods
proyectos = repo.obtener_proyectos()
equipos = repo.obtener_equipos(proyecto_id=1)
```

### Injecting Repository into Application

The repository should be injected from `main_qt.py` into `AppGUI`:

```python
# In main_qt.py
from repo import SQLiteRepository

# Create repository instance
repo = SQLiteRepository(db_path)

# Pass to AppGUI
app_gui = AppGUI(repo=repo, config=config)
```

### Switching Between Backends

To switch from SQLite to Firebase (when implemented):

```python
# SQLite backend
from repo import SQLiteRepository
repo = SQLiteRepository(db_path="progain_database.db")

# Firebase backend (future implementation)
from repo import FirestoreRepository
repo = FirestoreRepository(
    service_account_path="serviceAccount.json",
    project_id="my-firebase-project"
)
```

## Repository Interface

All repository implementations must implement the `BaseRepository` interface, which includes methods for:

### Proyecto (Project) Operations
- `obtener_proyectos()` - Get all projects
- `obtener_proyecto_por_id(proyecto_id)` - Get project by ID

### Equipo (Equipment) Operations
- `obtener_equipos(proyecto_id)` - Get equipment for project
- `obtener_equipo_por_id(equipo_id)` - Get equipment by ID
- `guardar_equipo(datos, equipo_id=None)` - Save/update equipment
- `eliminar_equipo(equipo_id)` - Delete equipment

### Transacción (Transaction) Operations
- `obtener_transaccion_por_id(transaccion_id)` - Get transaction by ID
- `obtener_transacciones_por_proyecto(proyecto_id, filtros=None)` - Get transactions with filters
- `crear_nuevo_alquiler(datos)` - Create new rental
- `actualizar_alquiler(transaccion_id, datos)` - Update rental
- `eliminar_alquiler(alquiler_id)` - Delete rental

### Entidad (Entity - Clientes/Operadores) Operations
- `obtener_clientes_por_proyecto(proyecto_id)` - Get clients
- `obtener_operadores_por_proyecto(proyecto_id)` - Get operators
- `obtener_entidades_equipo_por_tipo(proyecto_id, tipo_entidad)` - Get entities by type

### Mantenimiento (Maintenance) Operations
- `registrar_mantenimiento(datos)` - Register maintenance
- `actualizar_mantenimiento(datos)` - Update maintenance
- `eliminar_mantenimiento(mantenimiento_id)` - Delete maintenance
- `obtener_mantenimientos_por_equipo(equipo_id, limite=200)` - Get maintenance records

### Abono/Pago (Payment) Operations
- `registrar_abono_general_cliente(datos_pago)` - Register client payment
- `actualizar_abono(pago_id, nueva_fecha, nuevo_monto, nuevo_comentario)` - Update payment
- `eliminar_abono(pago_ids)` - Delete payments
- `obtener_lista_abonos(proyecto_id, filtros)` - Get payments with filters

### Dashboard & Analytics
- `obtener_kpis_dashboard(proyecto_id, anio, mes, equipo_id=None)` - Get dashboard KPIs

### Utility Methods
- `crear_tablas_nucleo()` - Create core tables
- `asegurar_tabla_pagos()` - Ensure payments table exists
- `asegurar_tabla_mantenimientos()` - Ensure maintenance table exists
- `asegurar_tabla_alquiler_meta()` - Ensure rental metadata table exists

## Testing

Run repository tests:

```bash
python -m unittest tests.test_sqlite_repo -v
```

## Future Work

### Firebase Firestore Implementation

The `FirestoreRepository` class is currently a skeleton. It will be implemented in future PRs with:

1. Firebase Admin SDK integration
2. Collection mapping (SQLite tables → Firestore collections)
3. Type conversion (SQLite types → Firestore types)
4. Storage integration for attachments
5. Transaction support
6. Query optimization

### Migration Tool

A migration tool will be provided to migrate data from SQLite to Firestore:

- See PR: `feature/firebase-migrator`
- GUI dialog for migration: `feature/migracion-ui`

## Benefits of Repository Pattern

1. **Separation of Concerns**: Business logic is decoupled from data access
2. **Testability**: Easy to mock repositories for unit testing
3. **Flexibility**: Can switch backends without changing UI code
4. **Maintainability**: Changes to data layer don't affect business logic
5. **Migration Support**: Enables gradual migration from SQLite to Firebase

## Notes

- The SQLite repository wraps the existing `DatabaseManager` from `logic.py`
- Existing code continues to work without changes
- Migration to use repository is gradual and incremental
- Firebase support will be added in future PRs after migration infrastructure is in place
