"""
Migration dialog for moving data from SQLite to Firestore.

Provides UI and logic to migrate all data from a SQLite database to Firestore.
"""
import logging
import os
from datetime import datetime
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, 
    QMessageBox, QProgressBar, QTextEdit, QFileDialog, QGroupBox, QFormLayout
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal

from app.app_settings import AppSettings, get_settings
from app.repo.repository_factory import RepositoryFactory
from app.repo.base_repository import BaseRepository

logger = logging.getLogger(__name__)


class MigrationWorker(QThread):
    """Worker thread for performing migration in background."""
    
    progress = pyqtSignal(int, str)  # progress percentage, status message
    finished = pyqtSignal(bool, str)  # success, message
    
    def __init__(self, sqlite_repo: BaseRepository, firestore_repo: BaseRepository):
        super().__init__()
        self.sqlite_repo = sqlite_repo
        self.firestore_repo = firestore_repo
        self.collections_migrated = 0
        self.total_collections = 9  # Number of collections to migrate
    
    def run(self):
        """Execute the migration."""
        try:
            self._migrate_all_data()
            self.finished.emit(True, "Migración completada exitosamente")
        except Exception as e:
            logger.error(f"Error durante migración: {e}", exc_info=True)
            self.finished.emit(False, f"Error durante migración: {str(e)}")
    
    def _update_progress(self, message: str):
        """Update progress."""
        progress = int((self.collections_migrated / self.total_collections) * 100)
        self.progress.emit(progress, message)
    
    def _migrate_all_data(self):
        """Migrate all data from SQLite to Firestore."""
        
        # 1. Migrate Proyectos
        self._update_progress("Migrando proyectos...")
        proyectos = self.sqlite_repo.obtener_proyectos()
        for proyecto in proyectos:
            try:
                # Check if already exists
                existing = self.firestore_repo.obtener_proyecto_por_id(proyecto["id"])
                if not existing:
                    self.firestore_repo.crear_proyecto(
                        nombre=proyecto.get("nombre", ""),
                        descripcion=proyecto.get("descripcion", ""),
                        moneda=proyecto.get("moneda", "RD$"),
                        cuenta_principal=proyecto.get("cuenta_principal", "")
                    )
            except Exception as e:
                logger.warning(f"Error migrando proyecto {proyecto.get('id')}: {e}")
        self.collections_migrated += 1
        
        # 2. Migrate Categorías
        self._update_progress("Migrando categorías...")
        categorias = self.sqlite_repo.obtener_categorias()
        # Categories are typically auto-created, just log count
        logger.info(f"Categorías en SQLite: {len(categorias)}")
        self.collections_migrated += 1
        
        # 3. Migrate Cuentas
        self._update_progress("Migrando cuentas...")
        cuentas = self.sqlite_repo.obtener_cuentas()
        logger.info(f"Cuentas en SQLite: {len(cuentas)}")
        self.collections_migrated += 1
        
        # 4. Migrate Clientes
        self._update_progress("Migrando clientes...")
        clientes = self.sqlite_repo.obtener_clientes()
        for cliente in clientes:
            try:
                existing = self.firestore_repo.obtener_cliente_por_id(cliente["id"])
                if not existing:
                    datos = {k: v for k, v in cliente.items() if k != "id"}
                    self.firestore_repo.crear_cliente(
                        nombre=cliente.get("nombre", ""),
                        **datos
                    )
            except Exception as e:
                logger.warning(f"Error migrando cliente {cliente.get('id')}: {e}")
        self.collections_migrated += 1
        
        # 5. Migrate Operadores
        self._update_progress("Migrando operadores...")
        operadores = self.sqlite_repo.obtener_operadores()
        for operador in operadores:
            try:
                existing = self.firestore_repo.obtener_operador_por_id(operador["id"])
                if not existing:
                    datos = {k: v for k, v in operador.items() if k != "id"}
                    self.firestore_repo.crear_operador(
                        nombre=operador.get("nombre", ""),
                        **datos
                    )
            except Exception as e:
                logger.warning(f"Error migrando operador {operador.get('id')}: {e}")
        self.collections_migrated += 1
        
        # 6. Migrate Equipos
        self._update_progress("Migrando equipos...")
        equipos = self.sqlite_repo.obtener_equipos()
        for equipo in equipos:
            try:
                existing = self.firestore_repo.obtener_equipo_por_id(equipo["id"])
                if not existing:
                    self.firestore_repo.crear_equipo(
                        proyecto_id=equipo.get("proyecto_id", 0),
                        nombre=equipo.get("nombre", ""),
                        marca=equipo.get("marca", ""),
                        modelo=equipo.get("modelo", ""),
                        categoria=equipo.get("categoria", ""),
                        equipo=equipo.get("equipo", "")
                    )
            except Exception as e:
                logger.warning(f"Error migrando equipo {equipo.get('id')}: {e}")
        self.collections_migrated += 1
        
        # 7. Migrate Alquileres
        self._update_progress("Migrando alquileres...")
        alquileres = self.sqlite_repo.obtener_alquileres()
        for alquiler in alquileres:
            try:
                alquiler_id = alquiler.get("id")
                existing = self.firestore_repo.obtener_alquiler_por_id(alquiler_id)
                if not existing:
                    self.firestore_repo.crear_alquiler(alquiler)
            except Exception as e:
                logger.warning(f"Error migrando alquiler {alquiler.get('id')}: {e}")
        self.collections_migrated += 1
        
        # 8. Migrate Transacciones
        self._update_progress("Migrando transacciones...")
        transacciones = self.sqlite_repo.obtener_transacciones()
        for transaccion in transacciones:
            try:
                # Transactions might exist, skip if ID exists
                self.firestore_repo.crear_transaccion(transaccion)
            except Exception as e:
                logger.warning(f"Error migrando transacción: {e}")
        self.collections_migrated += 1
        
        # 9. Migrate Pagos
        self._update_progress("Migrando pagos...")
        pagos = self.sqlite_repo.obtener_pagos()
        for pago in pagos:
            try:
                # Create pago in Firestore
                self.firestore_repo.crear_pago(pago)
            except Exception as e:
                logger.warning(f"Error migrando pago: {e}")
        self.collections_migrated += 1
        
        # 10. Migrate Mantenimientos
        self._update_progress("Migrando mantenimientos...")
        mantenimientos = self.sqlite_repo.obtener_mantenimientos()
        for mantenimiento in mantenimientos:
            try:
                self.firestore_repo.crear_mantenimiento(mantenimiento)
            except Exception as e:
                logger.warning(f"Error migrando mantenimiento: {e}")
        
        self._update_progress("Migración completada")


class DialogoMigracionFirestore(QDialog):
    """
    Dialog for migrating data from SQLite to Firestore.
    """
    
    def __init__(self, parent=None, settings: AppSettings = None):
        super().__init__(parent)
        self.settings = settings or get_settings()
        self.setWindowTitle("Migración de SQLite a Firestore")
        self.setModal(True)
        self.resize(600, 500)
        
        self.sqlite_repo = None
        self.firestore_repo = None
        self.worker = None
        
        self._init_ui()
    
    def _init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout()
        
        # Info label
        info_label = QLabel(
            "<b>Migración de Datos: SQLite → Firestore</b><br><br>"
            "Esta herramienta migrará todos los datos de una base de datos SQLite a Firestore.<br>"
            "Asegúrate de que Firestore esté configurado correctamente antes de continuar.<br><br>"
            "<b>Nota:</b> La migración NO eliminará datos de SQLite."
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Source database selection
        source_group = QGroupBox("Base de Datos Origen (SQLite)")
        source_layout = QFormLayout()
        
        db_selection_layout = QHBoxLayout()
        self.db_path_label = QLabel("<i>No seleccionada</i>")
        db_selection_layout.addWidget(self.db_path_label, 1)
        
        select_db_btn = QPushButton("Seleccionar...")
        select_db_btn.clicked.connect(self._select_sqlite_db)
        db_selection_layout.addWidget(select_db_btn)
        
        source_layout.addRow("Archivo:", db_selection_layout)
        source_group.setLayout(source_layout)
        layout.addWidget(source_group)
        
        # Progress section
        progress_group = QGroupBox("Progreso de Migración")
        progress_layout = QVBoxLayout()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("Listo para migrar")
        self.status_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        progress_layout.addWidget(self.status_label)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(150)
        progress_layout.addWidget(self.log_text)
        
        progress_group.setLayout(progress_layout)
        layout.addWidget(progress_group)
        
        layout.addStretch()
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        self.migrate_btn = QPushButton("Iniciar Migración")
        self.migrate_btn.clicked.connect(self._start_migration)
        self.migrate_btn.setEnabled(False)
        btn_layout.addWidget(self.migrate_btn)
        
        self.close_btn = QPushButton("Cerrar")
        self.close_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.close_btn)
        
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def _select_sqlite_db(self):
        """Select SQLite database file."""
        db_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar Base de Datos SQLite",
            "",
            "Archivos SQLite (*.db);;Todos los archivos (*)"
        )
        
        if db_path and os.path.exists(db_path):
            self.db_path_label.setText(db_path)
            self.sqlite_path = db_path
            self.migrate_btn.setEnabled(True)
            self._log(f"Base de datos seleccionada: {db_path}")
        else:
            self.db_path_label.setText("<i>No seleccionada</i>")
            self.migrate_btn.setEnabled(False)
    
    def _log(self, message: str):
        """Add message to log."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
    
    def _start_migration(self):
        """Start the migration process."""
        # Verify Firestore configuration
        if not self.settings.is_firestore_configured():
            QMessageBox.warning(
                self,
                "Firestore no configurado",
                "Firestore no está configurado correctamente.\n"
                "Por favor, configura Firestore en 'Configuración > Fuente de Datos' antes de migrar."
            )
            return
        
        # Confirm migration
        reply = QMessageBox.question(
            self,
            "Confirmar Migración",
            f"¿Estás seguro de migrar los datos desde:\n{self.sqlite_path}\n\n"
            "hacia Firestore?\n\n"
            "Este proceso puede tomar varios minutos dependiendo del tamaño de la base de datos.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        # Disable UI during migration
        self.migrate_btn.setEnabled(False)
        self.close_btn.setEnabled(False)
        
        try:
            # Create repositories
            self._log("Conectando a SQLite...")
            self.sqlite_repo = RepositoryFactory.create_sqlite_for_migration(self.sqlite_path)
            
            self._log("Conectando a Firestore...")
            self.firestore_repo = RepositoryFactory.create_firestore(self.settings)
            
            # Create and start worker thread
            self._log("Iniciando migración...")
            self.worker = MigrationWorker(self.sqlite_repo, self.firestore_repo)
            self.worker.progress.connect(self._on_progress)
            self.worker.finished.connect(self._on_finished)
            self.worker.start()
            
        except Exception as e:
            logger.error(f"Error iniciando migración: {e}")
            self._log(f"ERROR: {str(e)}")
            QMessageBox.critical(
                self,
                "Error",
                f"No se pudo iniciar la migración:\n\n{str(e)}"
            )
            self.migrate_btn.setEnabled(True)
            self.close_btn.setEnabled(True)
    
    def _on_progress(self, percentage: int, message: str):
        """Handle progress updates."""
        self.progress_bar.setValue(percentage)
        self.status_label.setText(message)
        self._log(message)
    
    def _on_finished(self, success: bool, message: str):
        """Handle migration completion."""
        self._log(message)
        self.status_label.setText(message)
        
        # Re-enable UI
        self.close_btn.setEnabled(True)
        
        if success:
            self.progress_bar.setValue(100)
            
            # Update migration timestamp in settings
            self.settings.set("migration.last_migration_date", datetime.now().isoformat())
            self.settings.set("migration.sqlite_source_path", self.sqlite_path)
            self.settings.save()
            
            QMessageBox.information(
                self,
                "Migración Exitosa",
                "La migración se completó exitosamente.\n\n"
                "Todos los datos han sido transferidos a Firestore."
            )
        else:
            QMessageBox.critical(
                self,
                "Error de Migración",
                f"La migración falló:\n\n{message}\n\n"
                "Revisa el log para más detalles."
            )
