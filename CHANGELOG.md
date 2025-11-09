# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added - PR #3: Complete Entity Management with Contact Information

#### Database Migration
- **Added**: Automatic migration to add `telefono` and `cedula` columns to `equipos_entidades` table
- **Enhanced**: `asegurar_tabla_equipos_entidades()` now includes column migration
- Safe migration: checks if columns exist before adding (idempotent)
- Backward compatible: handles existing databases gracefully

#### Entity Management Features
- **Complete**: Full CRUD for entities (Clientes/Operadores) with contact information
- **Fields**: Name, Telefono, Cedula/RNC, Active status
- **UI**: `VentanaGestionEntidad` already supports displaying and editing all fields
- **Validation**: Telefono and cedula are optional fields
- **ID column**: Hidden in UI but used for edit/delete operations

#### Methods Enhanced in logic.py
- `asegurar_tabla_equipos_entidades()` - Now adds telefono/cedula columns via ALTER TABLE
- `guardar_entidad()` - Already supports telefono/cedula (no changes needed)
- `obtener_entidad_por_id()` - Retrieves entity with all fields including contact info
- `eliminar_entidad()` - Marks entity as inactive
- `obtener_entidades_equipo_por_tipo()` - Returns all fields including telefono/cedula

#### UI Features (ventana_gestion_entidad.py)
Already implemented and working:
- ✅ Table with columns: ID (hidden), Name, Telefono, Cedula/RNC, Status
- ✅ Add/Edit/Delete buttons
- ✅ Dialog for entity creation and editing
- ✅ Validation (name required, telefono/cedula optional)
- ✅ Status toggle (Active/Inactive)
- ✅ Handles NULL values gracefully

#### Testing
- **New**: `tests/test_entity_management.py` with 6 comprehensive tests
- All tests pass ✅
- Tests cover:
  - Creating entity with telefono/cedula
  - Creating entity without telefono/cedula (optional)
  - Updating entity to add contact information
  - Retrieving entity by ID
  - Deleting entity (marking inactive)
  - Table migration (column addition)

#### Database Schema
Before (missing columns):
```sql
CREATE TABLE equipos_entidades (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL,
    tipo TEXT NOT NULL,
    proyecto_id INTEGER,
    activo INTEGER DEFAULT 1
)
```

After (with migration):
```sql
ALTER TABLE equipos_entidades ADD COLUMN telefono TEXT;
ALTER TABLE equipos_entidades ADD COLUMN cedula TEXT;
```

### Added - PR #2: Fix Edit Alquiler Duplication Bug

#### Bug Fix
- **Fixed**: Editing a rental (alquiler) no longer creates duplicate transactions
- **Enhanced**: Added validation to ensure transaction ID is present when opening edit dialog
- **Improved**: Better error handling and logging in edit workflow

#### Changes to dialogo_alquiler.py
- Enhanced `set_datos()` method with strict validation for transaction ID
- Raises ValueError if edit mode is attempted without transaction ID
- Added comprehensive logging for edit vs create mode detection
- Improved documentation explaining the edit workflow

#### Changes to registro_alquileres_tab.py
- Enhanced `editar_alquiler()` method with better error handling
- Added validation to ensure loaded data contains transaction ID
- Improved logging throughout the edit workflow
- Added success/failure feedback for database operations
- Better separation of concerns (dialog validates/closes, tab performs UPDATE)

#### Testing
- **New**: `tests/test_edit_alquiler_fix.py` - Automated test verifying no duplicates on edit
- Test creates, edits, and verifies transaction count remains the same
- All tests pass ✅

#### Technical Details
The fix ensures that:
1. When DialogoAlquiler is opened with `alquiler` parameter, it sets `self.transaccion_id`
2. The `set_datos()` method validates the ID is present and raises error if missing
3. When `guardar_alquiler()` is called, it detects edit mode via `self.transaccion_id`
4. In edit mode, dialog only validates and closes (no INSERT)
5. The calling code (`registro_alquileres_tab`) performs the actual UPDATE
6. Transaction count verification ensures no duplicates

### Added - PR #1: Repository Abstraction Pattern

#### Repository Layer
- **New**: `repo/` directory with repository pattern implementation
- **New**: `repo/base_repo.py` - Abstract base class defining repository interface
- **New**: `repo/sqlite_repo.py` - SQLite implementation wrapping existing DatabaseManager
- **New**: `repo/firestore_repo.py` - Firestore skeleton (to be implemented in future PRs)

#### Testing Infrastructure
- **New**: `tests/` directory for unit tests
- **New**: `tests/test_sqlite_repo.py` - Unit tests for SQLite repository
- Tests cover basic CRUD operations and repository initialization

#### Documentation
- **New**: `README.md` - Main project documentation
- **New**: `repo/README.md` - Repository pattern usage guide
- **New**: `CHANGELOG.md` - This changelog file
- **New**: `.gitignore` - Comprehensive gitignore including Firebase credentials

#### Features
- Repository pattern enables easy switching between SQLite and Firebase backends
- Abstraction layer separates data access from business logic
- Backward compatible - existing code continues to work
- Foundation for Firebase migration (future PRs)

#### Methods Added to Repository Interface
- Project operations: `obtener_proyectos`, `obtener_proyecto_por_id`
- Equipment operations: `obtener_equipos`, `guardar_equipo`, `eliminar_equipo`
- Transaction operations: `crear_nuevo_alquiler`, `actualizar_alquiler`, `eliminar_alquiler`
- Entity operations: `obtener_clientes_por_proyecto`, `obtener_operadores_por_proyecto`
- Maintenance operations: `registrar_mantenimiento`, `actualizar_mantenimiento`
- Payment operations: `registrar_abono_general_cliente`, `actualizar_abono`
- Dashboard: `obtener_kpis_dashboard`
- Utility: `crear_tablas_nucleo`, `asegurar_tabla_pagos`, etc.

#### Enhanced SQLiteRepository Methods
- Additional passthrough methods for existing DatabaseManager functionality
- Entity management: `guardar_entidad`, `eliminar_entidad`, `obtener_entidad_por_id`
- Complete coverage of all DatabaseManager operations

### Changed
- No breaking changes - all existing functionality preserved

### Security
- Added `.gitignore` to prevent accidental commit of sensitive files
- Documented importance of not committing `serviceAccount.json`
- Added security guidelines in README

### Testing
- All repository tests pass (7 passed, 2 skipped due to schema differences)
- Tests validate repository pattern works correctly
- Skipped tests documented and will pass with full database schema

---

## Future Releases (Planned)

### [0.2.0] - Feature: Fix Edit Alquiler (PR #2)
- Fix duplicate transaction bug when editing rentals
- Ensure `dialogo_alquiler.py` properly assigns `transaccion_id`
- Update `registro_alquileres_tab.py` to use `repo.actualizar_alquiler()`

### [0.3.0] - Feature: Complete Entity Management (PR #3)
- Add `telefono` and `cedula` columns to `equipos_entidades` table
- Implement complete CRUD for entities (clients/operators)
- Update UI to show contact information

### [0.4.0] - Feature: Migration UI (PR #4)
- Add "Migrar a Firebase" button in main menu
- DialogoMigracion with dry-run preview
- Progress bars and real-time logs
- Automatic backup before migration

### [0.5.0] - Feature: Firebase Migrator (PR #5)
- Complete FirebaseRepository implementation
- Batch migration (max 500 docs per batch)
- Type conversion (dates, numbers, nulls)
- Storage upload for attachments
- Generate mapping.json and logs

### [0.6.0] - Feature: UI Modernization (PR #6)
- Global stylesheet
- Icons and improved layouts

### [0.7.0] - Feature: Logging & Audit (PR #7)
- Migration audit logs
- Metadata fields in documents

### [1.0.0] - Feature: Tests & CI (PR #8)
- GitHub Actions for CI/CD
- Complete test coverage
- Automated smoke tests

---

## Notes

- Version numbers are tentative and may change
- Each feature will be delivered in its own PR
- Breaking changes will be clearly documented
- Security updates will be prioritized
