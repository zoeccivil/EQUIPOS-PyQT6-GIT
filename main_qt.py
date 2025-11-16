import sys
import os
import logging
import traceback
import time  # Import consolidado
from PyQt6.QtWidgets import QApplication, QFileDialog, QMessageBox, QDialog

from logic import DatabaseManager
from config_manager import cargar_configuracion, guardar_configuracion
from app_gui_qt import AppGUI

# New Firestore-first architecture imports
from app.app_settings import get_settings, AppSettings
from app.repo.repository_factory import RepositoryFactory
from app.ui.data_source_widget import DataSourceWidget

# Configurar logging global (archivo ya usado por el proyecto)
LOG_FILE = "progain.log"
logging.basicConfig(
    filename=LOG_FILE,
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)s %(message)s"
)
logger = logging.getLogger(__name__)


def excepthook(exc_type, exc_value, exc_tb):
    """
    Manejador global de excepciones: registra la traza completa en el log
    y muestra un QMessageBox si es posible. Finalmente sale con código 1.
    """
    msg = "".join(traceback.format_exception(exc_type, exc_value, exc_tb))
    logger.exception("Excepción no controlada:\n%s", msg)

    # Intentar mostrar un dialogo si la app GUI está disponible.
    try:
        app = QApplication.instance()
        created_temp_app = False
        if app is None:
            # Crear una QApplication temporal para poder mostrar el QMessageBox
            app = QApplication([])  # no manipulamos sys.argv aquí
            created_temp_app = True

        QMessageBox.critical(None, "Error inesperado",
                             "Se produjo un error inesperado y la aplicación debe cerrarse.\n\n"
                             f"{exc_value}")

        if created_temp_app:
            # Forzar cierre de la app temporal que creamos
            app.quit()
    except Exception as show_err:
        # Si no se puede mostrar el QMessageBox, al menos imprimir en consola
        logger.exception("No se pudo mostrar QMessageBox en excepthook: %s", show_err)
        try:
            print("Error inesperado:", exc_value, file=sys.stderr)
        except Exception:
            pass

    # Llamar al excepthook original por si hay otras integraciones
    try:
        sys.__excepthook__(exc_type, exc_value, exc_tb)
    except Exception:
        pass

    # Asegurar salida
    sys.exit(1)


# En: main_qt.py
# REEMPLAZA la función sync_from_firestore_to_sqlite completa

def sync_from_firestore_to_sqlite(firestore_repo, sqlite_db_manager):
    """
    Sincroniza las 8 tablas críticas definidas por el usuario,
    incluyendo transacciones, con un delay de 0.3s.
    """
    logger.info("Sincronizando 8 tablas CRÍTICAS (plan de usuario)...")
    
    # --- Tu Lista de 8 Tablas Críticas ---
    tablas_esenciales_sync = [
        'proyectos', 
        'categorias', 
        'subcategorias',
        'cuentas', 
        'equipos', 
        'equipos_entidades',
        'transacciones',            # <-- Tabla grande añadida
        'equipos_alquiler_meta'     # <-- Tabla grande añadida
    ]
    
    logger.warning(
        f"Omitiendo 19 tablas secundarias para Carga Bajo Demanda."
    )
    
    synced_count = 0
    failed_tables = []
    
    for tabla in tablas_esenciales_sync:
        try:
            logger.info(f"Sincronizando tabla esencial: {tabla}...")
            
            columnas_sqlite = sqlite_db_manager.obtener_columnas_de_tabla(tabla)
            if not columnas_sqlite:
                logger.warning(f"No se pudieron obtener columnas para la tabla SQLite '{tabla}'. Omitiendo.")
                continue

            mapa_columnas = {}
            for col_sqlite in columnas_sqlite:
                partes = col_sqlite.split('_')
                col_camel = partes[0] + ''.join(p.capitalize() for p in partes[1:])
                mapa_columnas[col_sqlite] = [col_sqlite, col_camel]

            # Esta llamada puede tardar mucho para 'transacciones'
            registros_fs = firestore_repo.obtener_tabla_completa(tabla)
            
            if registros_fs:
                registros_insertados_count = 0
                for registro_fs_raw in registros_fs:
                    try:
                        registro_fs_limpio = {k: v for k, v in registro_fs_raw.items() if not k.startswith('_firestore')}
                        datos_a_insertar = {}
                        
                        for col_sqlite, posibles_nombres_fs in mapa_columnas.items():
                            if posibles_nombres_fs[0] in registro_fs_limpio:
                                datos_a_insertar[col_sqlite] = registro_fs_limpio[posibles_nombres_fs[0]]
                            elif posibles_nombres_fs[1] in registro_fs_limpio:
                                datos_a_insertar[col_sqlite] = registro_fs_limpio[posibles_nombres_fs[1]]
                        
                        if not datos_a_insertar:
                            continue

                        columns = list(datos_a_insertar.keys())
                        placeholders = ', '.join(['?' for _ in columns])
                        column_names = ', '.join(columns)
                        query = f"INSERT OR REPLACE INTO {tabla} ({column_names}) VALUES ({placeholders})"
                        
                        values = []
                        for col in columns:
                            val = datos_a_insertar[col]
                            if isinstance(val, str) and (col.endswith('_id') or col == 'id'):
                                try: values.append(int(val))
                                except (ValueError, TypeError): values.append(val)
                            else:
                                values.append(val)
                        
                        sqlite_db_manager.execute(query, values)
                        registros_insertados_count += 1
                    except Exception as e:
                        logger.warning(f"Error insertando registro individual en {tabla} (ID: {registro_fs_raw.get('id', 'N/A')}): {e}")
                        continue
                
                if registros_insertados_count > 0:
                    logger.info(f"✓ Sincronizadas e insertadas {registros_insertados_count} / {len(registros_fs)} registros de {tabla}")
                else:
                    logger.debug(f"○ Tabla {tabla} vacía, omitida")

                synced_count += registros_insertados_count
                
                # --- Tu Pausa de 0.3 segundos ---
                logger.debug("Esperando 0.3 seg...")
                time.sleep(0.3) 

        except Exception as e:
            # Si esto falla con 429 para 'transacciones', tu plan no funcionó
            logger.error(f"✗ Error fatal sincronizando tabla {tabla}: {e}", exc_info=True)
            failed_tables.append(tabla)
            time.sleep(0.3)
            continue
    
    if failed_tables:
        logger.warning(f"Tablas esenciales con errores de sincronización: {', '.join(failed_tables)}")
    
    logger.info(f"Sincronización esencial completada: {synced_count} registros sincronizados")
    return synced_count, failed_tables

def solicitar_bd_por_dialogo():
    """
    Muestra un QFileDialog para seleccionar una base de datos SQLite.
    Retorna la ruta seleccionada o None si el usuario cancela.
    """
    file_path, _ = QFileDialog.getOpenFileName(
        None,
        "Seleccionar base de datos",
        "",
        "Archivos SQLite (*.db);;Todos los archivos (*)"
    )
    return file_path or None


def main():
    # Registrar el manejador global de excepciones
    sys.excepthook = excepthook

    # Crear la aplicación Qt
    app = QApplication(sys.argv)

    # Load new app settings (Firestore-first architecture)
    logger.info("Cargando configuración de la aplicación...")
    settings = get_settings()
    
    # Load legacy config for backward compatibility (e.g., carpeta_conduces)
    try:
        legacy_config = cargar_configuracion()
    except Exception as e:
        logger.exception("No se pudo cargar la configuración legacy: %s", e)
        legacy_config = {}

    # Determine data source: Firestore or SQLite
    data_source = settings.get_data_source()
    logger.info(f"Fuente de datos configurada: {data_source}")
    
    # Initialize repository based on configured data source
    repository = None
    db_manager = None  # For backward compatibility with tabs that still use it
    actual_data_source = data_source  # Track which source is actually being used
    
    if data_source == "firestore":
        # FIRESTORE MODE: Firestore is the primary data source
        logger.info("Inicializando Firestore como fuente de datos principal...")
        
        # Check if Firestore is properly configured
        if not settings.is_firestore_configured():
            logger.warning("Firestore no está configurado correctamente")
            reply = QMessageBox.warning(
                None,
                "Firestore no configurado",
                "Firestore no está configurado como fuente de datos principal.\n\n"
                "¿Deseas configurarlo ahora?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No | QMessageBox.StandardButton.Cancel
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                # Show configuration dialog
                config_dialog = DataSourceWidget(None, settings)
                if config_dialog.exec() != QDialog.DialogCode.Accepted:
                    logger.warning("Usuario canceló la configuración de Firestore, usando modo SQLite")
                    # Fall back to SQLite mode instead of exiting
                    data_source = "sqlite"
                    actual_data_source = "sqlite"
                else:
                    # Reload settings after configuration
                    settings = get_settings()
            elif reply == QMessageBox.StandardButton.No:
                logger.warning("Usuario decidió no configurar Firestore, usando modo SQLite")
                # Fall back to SQLite mode instead of exiting
                data_source = "sqlite"
                actual_data_source = "sqlite"
            else:
                # User cancelled, fall back to SQLite
                logger.warning("Usuario canceló, usando modo SQLite")
                data_source = "sqlite"
                actual_data_source = "sqlite"
        
        # Try to connect to Firestore (only if we're still in firestore mode)
        if data_source == "firestore":
            try:
                logger.info("Conectando a Firestore...")
                repository = RepositoryFactory.create_from_settings(settings)
                logger.info("Conexión a Firestore establecida exitosamente")
                
            except ConnectionError as e:
                logger.error(f"Error de conexión a Firestore: {e}")
                reply = QMessageBox.warning(
                    None,
                    "Error de Conexión Firestore",
                    f"No se pudo conectar a Firestore:\n\n{str(e)}\n\n"
                    "¿Deseas continuar con SQLite en modo local?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.Yes:
                    logger.info("Usuario eligió continuar con SQLite")
                    data_source = "sqlite"
                    actual_data_source = "sqlite (fallback)"
                else:
                    logger.info("Usuario decidió no continuar")
                    sys.exit(0)
            except Exception as e:
                logger.exception(f"Error inesperado al conectar a Firestore: {e}")
                reply = QMessageBox.warning(
                    None,
                    "Error Firestore",
                    f"Error al inicializar Firestore:\n\n{str(e)}\n\n"
                    "¿Deseas continuar con SQLite en modo local?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.Yes:
                    logger.info("Usuario eligió continuar con SQLite")
                    data_source = "sqlite"
                    actual_data_source = "sqlite (fallback)"
                else:
                    logger.info("Usuario decidió no continuar")
                    sys.exit(0)
    
    if data_source == "sqlite":
        # SQLITE MODE: SQLite is the data source (legacy or for testing)
        logger.info("Inicializando SQLite como fuente de datos...")
        
        db_path = settings.get_sqlite_path()
        
        # If database doesn't exist, ask user to select one
        if not os.path.isfile(db_path):
            reply = QMessageBox.question(
                None, 
                "Base de datos no encontrada",
                f"No se encontró la base de datos:\n{db_path}\n\n"
                "¿Deseas seleccionar una base de datos SQLite existente?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                selected = solicitar_bd_por_dialogo()
                if selected and os.path.isfile(selected):
                    db_path = selected
                    settings.set_sqlite_path(db_path)
                    settings.save()
                else:
                    logger.warning("No se seleccionó una base de datos válida")
                    db_path = ":memory:"  # Use in-memory database as fallback
                    actual_data_source = "sqlite (memoria)"
            else:
                logger.info("Usuario decidió no seleccionar base de datos, usando memoria")
                db_path = ":memory:"
                actual_data_source = "sqlite (memoria)"
        
        # Create SQLite repository
        try:
            repository = RepositoryFactory.create_sqlite(settings, db_path)
            
            # Also create legacy DatabaseManager for backward compatibility
            db_manager = DatabaseManager(db_path)
            
            # Initialize all tables - wrapped individually to avoid crashes
            def _init_table_safe(func, name):
                """Initialize a table safely without crashing."""
                try:
                    func()
                    logger.info(f"✓ Tabla inicializada: {name}")
                except Exception as e:
                    logger.warning(f"✗ Error inicializando tabla {name}: {e}")
            
            _init_table_safe(db_manager.crear_tablas_nucleo, "tablas nucleo")
            _init_table_safe(db_manager.sembrar_datos_iniciales, "datos iniciales")
            _init_table_safe(db_manager.crear_tabla_equipos, "equipos")
            _init_table_safe(db_manager.asegurar_tabla_alquiler_meta, "alquiler_meta")
            _init_table_safe(db_manager.asegurar_tabla_pagos, "pagos")
            _init_table_safe(db_manager.asegurar_tabla_mantenimientos, "mantenimientos")
            _init_table_safe(db_manager.asegurar_tablas_mantenimiento, "mantenimiento")
            _init_table_safe(db_manager.crear_indices, "indices")
            _init_table_safe(db_manager.asegurar_tabla_equipos_entidades, "equipos_entidades")
            
            logger.info(f"SQLite inicializado exitosamente en: {db_path}")
            
        except Exception as e:
            logger.exception(f"Error inicializando SQLite: {e}")
            QMessageBox.warning(
                None,
                "Error BD SQLite",
                f"No se pudo abrir la base de datos:\n{db_path}\n\n{e}\n\n"
                "Continuando con base de datos en memoria."
            )
            # Create in-memory database as last resort
            db_path = ":memory:"
            actual_data_source = "sqlite (memoria)"
            try:
                repository = RepositoryFactory.create_sqlite(settings, db_path)
                db_manager = DatabaseManager(db_path)
                db_manager.crear_tablas_nucleo()
                db_manager.sembrar_datos_iniciales()
            except Exception as e2:
                logger.exception(f"Error crítico creando base de datos en memoria: {e2}")
                QMessageBox.critical(None, "Error Crítico", f"No se pudo inicializar la aplicación:\n{e2}")
                sys.exit(1)
    
    # Create legacy config dict for AppGUI compatibility
    config = {
        "database_path": settings.get_sqlite_path() if data_source == "sqlite" else ":memory:",
        "carpeta_conduces": legacy_config.get("carpeta_conduces", ""),
        "data_source_display": actual_data_source  # Add data source indicator
    }
    
    # If we're using Firestore, create a temporary DatabaseManager for tabs that still need it
    # This is a transitional measure until all tabs are updated to use Repository
    if actual_data_source.startswith("firestore") and db_manager is None:
        # Create a temporary in-memory SQLite database for compatibility
        # Tabs will eventually be updated to use repository instead
        logger.info("Creando DatabaseManager temporal para compatibilidad con tabs...")
        db_manager = DatabaseManager(":memory:")
        
        # Initialize all tables - wrapped individually to avoid crashes
        def _init_table_safe(func, name):
            """Initialize a table safely without crashing."""
            try:
                func()
                logger.info(f"✓ Tabla temporal inicializada: {name}")
            except Exception as e:
                logger.warning(f"✗ Error inicializando tabla temporal {name}: {e}")
        
        _init_table_safe(db_manager.crear_tablas_nucleo, "tablas nucleo")
        _init_table_safe(db_manager.sembrar_datos_iniciales, "datos iniciales")
        _init_table_safe(db_manager.crear_tabla_equipos, "equipos")
        _init_table_safe(db_manager.asegurar_tabla_alquiler_meta, "alquiler_meta")
        _init_table_safe(db_manager.asegurar_tabla_pagos, "pagos")
        _init_table_safe(db_manager.asegurar_tabla_mantenimientos, "mantenimientos")
        _init_table_safe(db_manager.asegurar_tablas_mantenimiento, "mantenimiento")
        _init_table_safe(db_manager.crear_indices, "indices")
        _init_table_safe(db_manager.asegurar_tabla_equipos_entidades, "equipos_entidades")
        
        # Sync data from Firestore to the temporary SQLite database
        # This makes migrated data visible in tabs
        logger.info("Sincronizando datos desde Firestore a base de datos temporal...")
        try:
            synced, failed = sync_from_firestore_to_sqlite(repository, db_manager)
            if synced > 0:
                logger.info(f"✓ Sincronización exitosa: {synced} registros disponibles en tabs")
            if failed:
                logger.warning(f"Algunas tablas no se sincronizaron: {', '.join(failed)}")
        except Exception as e:
            logger.error(f"Error durante sincronización Firestore→SQLite: {e}")
            logger.warning("La app continuará, pero los datos podrían no estar visibles en tabs")


    # Start the main window
    try:
        window = AppGUI(db_manager, config, repository=repository, settings=settings)
        window.show()
    except Exception as e:
        logger.exception("Error creando ventana principal AppGUI: %s", e)
        QMessageBox.critical(
            None, 
            "Error al iniciar", 
            f"No se pudo iniciar la interfaz gráfica:\n{e}"
        )
        sys.exit(1)

    # Run Qt event loop
    try:
        exit_code = app.exec()
        logger.info("Aplicación finalizada con exit_code=%s", exit_code)
        
        # Cleanup
        if repository:
            repository.cerrar()
        
        sys.exit(exit_code)
    except Exception as e:
        logger.exception("Error durante app.exec(): %s", e)
        raise


if __name__ == "__main__":
    try:
        main()
    except SystemExit:
        # permitir salida normal con código
        raise
    except Exception as e:
        # Si ocurre algo aquí, el excepthook lo registrará; aserguramos que se imprima también.
        logger.exception("Fallo en main (capturado en __main__): %s", e)
        try:
            # Intentar mostrar un mensaje de error simple al usuario
            app = QApplication.instance() or QApplication(sys.argv)
            QMessageBox.critical(None, "Error crítico", f"Fallo crítico: {e}")
        except Exception:
            pass
        sys.exit(1)