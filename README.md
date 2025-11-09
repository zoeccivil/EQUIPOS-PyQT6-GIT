# EQUIPOS PyQt6 - Gestión de Proyectos, Equipos y Alquileres

Sistema de gestión para proyectos de construcción con equipos pesados, alquileres, operadores y clientes.

## Características

- Gestión de proyectos y equipos
- Registro de alquileres y transacciones
- Control de clientes y operadores
- Mantenimiento de equipos
- Pagos y abonos
- Dashboard con KPIs
- Reportes y análisis
- Adjuntos y conduces

## Requisitos

- Python 3.8+
- PyQt6
- SQLite3 (incluido con Python)

## Instalación

```bash
# Clonar repositorio
git clone https://github.com/zoeccivil/EQUIPOS-PyQT6-GIT.git
cd EQUIPOS-PyQT6-GIT

# Instalar dependencias (si existe requirements.txt)
pip install -r requirements.txt
```

## Uso

```bash
python main_qt.py
```

## Arquitectura

### Repository Pattern (Nuevo)

El proyecto ahora implementa el patrón Repository para abstraer la capa de persistencia:

- **SQLite**: Backend actual (por defecto)
- **Firebase Firestore**: Backend futuro (en desarrollo)

Ver documentación completa en [`repo/README.md`](repo/README.md)

### Estructura del Proyecto

```
├── main_qt.py              # Punto de entrada principal
├── app_gui_qt.py           # Interfaz gráfica principal
├── logic.py                # Lógica de negocio y DatabaseManager
├── repo/                   # Capa de repositorio (abstracción)
│   ├── base_repo.py        # Interfaz del repositorio
│   ├── sqlite_repo.py      # Implementación SQLite
│   └── firestore_repo.py   # Implementación Firebase (skeleton)
├── dialogo_alquiler.py     # Diálogo de alquileres
├── registro_alquileres_tab.py  # Tab de registro
├── ventana_gestion_*.py    # Ventanas de gestión
└── tests/                  # Tests unitarios
    └── test_sqlite_repo.py # Tests del repositorio
```

## Cambio de Backend de Persistencia

Para cambiar entre SQLite y Firebase (cuando esté disponible):

```python
# SQLite (actual)
from repo import SQLiteRepository
repo = SQLiteRepository("progain_database.db")

# Firebase (futuro)
from repo import FirestoreRepository
repo = FirestoreRepository(
    service_account_path="serviceAccount.json",
    project_id="mi-proyecto-firebase"
)
```

## Migración a Firebase

**Estado**: En desarrollo

La migración a Firebase Firestore incluirá:

1. **Interfaz de migración GUI** - Diálogo con opciones de migración
2. **Migrador automático** - Conversión batch de datos SQLite → Firestore
3. **Subida de adjuntos** - Storage para conduces y archivos
4. **Mapeo de IDs** - Trazabilidad entre SQLite y Firestore
5. **Dry-run mode** - Previsualización sin escribir datos
6. **Backup automático** - Respaldo antes de migrar

Ver PRs:
- `feature/migracion-ui` - Interfaz de migración
- `feature/firebase-migrator` - Lógica de migración

## Testing

```bash
# Ejecutar tests
python -m unittest discover tests -v

# Test específico de repositorio
python -m unittest tests.test_sqlite_repo -v
```

## Desarrollo

### Branches y PRs

El desarrollo sigue un modelo de feature branches:

- `feature/repo-abstraction` - Patrón Repository ✅
- `feature/fix-edit-alquiler` - Corrección edición alquileres
- `feature/entidades-complete` - Gestión completa de entidades
- `feature/migracion-ui` - UI de migración Firebase
- `feature/firebase-migrator` - Migrador Firebase
- `feature/ui-modernization` - Modernización UI
- `feature/logging-audit` - Auditoría y logs
- `feature/tests-ci` - CI/CD y tests

### Contribuir

1. Fork el repositorio
2. Crear branch de feature (`git checkout -b feature/nueva-caracteristica`)
3. Commit cambios (`git commit -am 'Añadir nueva característica'`)
4. Push al branch (`git push origin feature/nueva-caracteristica`)
5. Crear Pull Request

## Seguridad

### Credenciales Firebase

**IMPORTANTE**: NUNCA subir credenciales al repositorio

- Añadir `serviceAccount.json` a `.gitignore`
- Almacenar credenciales localmente fuera del repo
- Usar variables de entorno para configuración sensible

### .gitignore

Asegúrate de que `.gitignore` incluya:

```
# Firebase credentials
serviceAccount.json
firebase-credentials.json

# Database backups
backups/
*.db.backup

# Logs
*.log
progain.log

# Python
__pycache__/
*.pyc
.pytest_cache/
```

## Licencia

[Especificar licencia del proyecto]

## Contacto

[Información de contacto]

## Roadmap

### Versión Actual (SQLite)
- ✅ Gestión de proyectos
- ✅ Alquileres y transacciones
- ✅ Mantenimientos
- ✅ Pagos y abonos
- ✅ Dashboard y reportes
- ✅ Patrón Repository

### Próxima Versión (Firebase)
- 🔄 Migración automática SQLite → Firestore
- 🔄 Storage para adjuntos
- 🔄 Auth y seguridad
- 🔄 Backup en la nube
- 🔄 Sincronización multi-usuario
- 🔄 API REST (opcional)

### Mejoras Planificadas
- UI modernizada con estilos
- Tests completos con CI/CD
- Auditoría de cambios
- Monitoreo y observabilidad
- Optimización de performance

---

**Nota**: Este proyecto está en proceso de modernización para soportar Firebase Firestore como backend alternativo, manteniendo compatibilidad total con SQLite.
