"""
Backup dialog for creating SQLite backups from Firestore.

Provides UI and logic to backup Firestore data to SQLite files.
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


class BackupWorker(QThread):
    """Worker thread for performing backup in background."""
    
    progress = pyqtSignal(int, str)  # progress percentage, status message
    finished = pyqtSignal(bool, str)  # success, message
    
    def __init__(self, firestore_repo: BaseRepository, sqlite_repo: BaseRepository):
        super().__init__()
        self.firestore_repo = firestore_repo
        self.sqlite_repo = sqlite_repo
        self.collections_backed_up = 0
        self.total_collections = 9
    
    def run(self):
        """Execute the backup."""
        try:
            self._backup_all_data()
            self.finished.emit(True, "Backup completado exitosamente")
        except Exception as e:
            logger.error(f"Error durante backup: {e}", exc_info=True)
            self.finished.emit(False, f"Error durante backup: {str(e)}")
    
    def _update_progress(self, message: str):
        """Update progress."""
        progress = int((self.collections_backed_up / self.total_collections) * 100)
        self.progress.emit(progress, message)
    
    def _backup_all_data(self):
        """Backup all data from Firestore to SQLite."""
        
        # 1. Backup Proyectos
        self._update_progress("Respaldando proyectos...")
        proyectos = self.firestore_repo.obtener_proyectos()
        for proyecto in proyectos:
            try:
                self.sqlite_repo.crear_proyecto(
                    nombre=proyecto.get("nombre", ""),
                    descripcion=proyecto.get("descripcion", ""),
                    moneda=proyecto.get("moneda", "RD$"),
                    cuenta_principal=proyecto.get("cuenta_principal", "")
                )
            except Exception as e:
                logger.warning(f"Error respaldando proyecto: {e}")
        self.collections_backed_up += 1
        
        # 2. Backup Clientes
        self._update_progress("Respaldando clientes...")
        clientes = self.firestore_repo.obtener_clientes()
        for cliente in clientes:
            try:
                datos = {k: v for k, v in cliente.items() if k not in ["id", "_firestore_id"]}
                self.sqlite_repo.crear_cliente(
                    nombre=cliente.get("nombre", ""),
                    **datos
                )
            except Exception as e:
                logger.warning(f"Error respaldando cliente: {e}")
        self.collections_backed_up += 1
        
        # 3. Backup Operadores
        self._update_progress("Respaldando operadores...")
        operadores = self.firestore_repo.obtener_operadores()
        for operador in operadores:
            try:
                datos = {k: v for k, v in operador.items() if k not in ["id", "_firestore_id"]}
                self.sqlite_repo.crear_operador(
                    nombre=operador.get("nombre", ""),
                    **datos
                )
            except Exception as e:
                logger.warning(f"Error respaldando operador: {e}")
        self.collections_backed_up += 1
        
        # 4. Backup Equipos
        self._update_progress("Respaldando equipos...")
        equipos = self.firestore_repo.obtener_equipos()
        for equipo in equipos:
            try:
                self.sqlite_repo.crear_equipo(
                    proyecto_id=equipo.get("proyecto_id", 0),
                    nombre=equipo.get("nombre", ""),
                    marca=equipo.get("marca", ""),
                    modelo=equipo.get("modelo", ""),
                    categoria=equipo.get("categoria", ""),
                    equipo=equipo.get("equipo", "")
                )
            except Exception as e:
                logger.warning(f"Error respaldando equipo: {e}")
        self.collections_backed_up += 1
        
        # 5. Backup Alquileres
        self._update_progress("Respaldando alquileres...")
        alquileres = self.firestore_repo.obtener_alquileres()
        for alquiler in alquileres:
            try:
                # Remove Firestore-specific fields
                datos = {k: v for k, v in alquiler.items() if k != "_firestore_id"}
                self.sqlite_repo.crear_alquiler(datos)
            except Exception as e:
                logger.warning(f"Error respaldando alquiler: {e}")
        self.collections_backed_up += 1
        
        # 6. Backup Transacciones
        self._update_progress("Respaldando transacciones...")
        transacciones = self.firestore_repo.obtener_transacciones()
        for transaccion in transacciones:
            try:
                datos = {k: v for k, v in transaccion.items() if k != "_firestore_id"}
                self.sqlite_repo.crear_transaccion(datos)
            except Exception as e:
                logger.warning(f"Error respaldando transacción: {e}")
        self.collections_backed_up += 1
        
        # 7. Backup Pagos
        self._update_progress("Respaldando pagos...")
        pagos = self.firestore_repo.obtener_pagos()
        for pago in pagos:
            try:
                datos = {k: v for k, v in pago.items() if k != "_firestore_id"}
                self.sqlite_repo.crear_pago(datos)
            except Exception as e:
                logger.warning(f"Error respaldando pago: {e}")
        self.collections_backed_up += 1
        
        # 8. Backup Mantenimientos
        self._update_progress("Respaldando mantenimientos...")
        mantenimientos = self.firestore_repo.obtener_mantenimientos()
        for mantenimiento in mantenimientos:
            try:
                datos = {k: v for k, v in mantenimiento.items() if k != "_firestore_id"}
                self.sqlite_repo.crear_mantenimiento(datos)
            except Exception as e:
                logger.warning(f"Error respaldando mantenimiento: {e}")
        self.collections_backed_up += 1
        
        self._update_progress("Backup completado")


class DialogoBackupSQLite(QDialog):
    """
    Dialog for creating SQLite backups from Firestore.
    """
    
    def __init__(self, parent=None, settings: AppSettings = None):
        super().__init__(parent)
        self.settings = settings or get_settings()
        self.setWindowTitle("Crear Backup SQLite desde Firestore")
        self.setModal(True)
        self.resize(600, 500)
        
        self.firestore_repo = None
        self.sqlite_repo = None
        self.worker = None
        
        self._init_ui()
        self._load_settings()
    
    def _init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout()
        
        # Info label
        info_label = QLabel(
            "<b>Backup de Datos: Firestore → SQLite</b><br><br>"
            "Esta herramienta creará un archivo de backup SQLite con todos los datos de Firestore.<br>"
            "El backup es útil para análisis offline o como respaldo de seguridad.<br><br>"
            "<b>Nota:</b> El backup NO afectará los datos en Firestore."
        )
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Backup location configuration
        location_group = QGroupBox("Ubicación del Backup")
        location_layout = QFormLayout()
        
        folder_selection_layout = QHBoxLayout()
        self.folder_label = QLabel("<i>No configurada</i>")
        folder_selection_layout.addWidget(self.folder_label, 1)
        
        select_folder_btn = QPushButton("Seleccionar...")
        select_folder_btn.clicked.connect(self._select_backup_folder)
        folder_selection_layout.addWidget(select_folder_btn)
        
        location_layout.addRow("Carpeta:", folder_selection_layout)
        
        self.filename_label = QLabel()
        location_layout.addRow("Archivo:", self.filename_label)
        
        location_group.setLayout(location_layout)
        layout.addWidget(location_group)
        
        # Progress section
        progress_group = QGroupBox("Progreso del Backup")
        progress_layout = QVBoxLayout()
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("Listo para crear backup")
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
        
        self.backup_btn = QPushButton("Crear Backup")
        self.backup_btn.clicked.connect(self._start_backup)
        self.backup_btn.setEnabled(False)
        btn_layout.addWidget(self.backup_btn)
        
        self.close_btn = QPushButton("Cerrar")
        self.close_btn.clicked.connect(self.reject)
        btn_layout.addWidget(self.close_btn)
        
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def _load_settings(self):
        """Load backup folder from settings."""
        backup_folder = self.settings.get_backup_folder()
        if backup_folder:
            self.folder_label.setText(backup_folder)
            self.backup_folder = backup_folder
            self._update_filename_preview()
            self.backup_btn.setEnabled(True)
    
    def _select_backup_folder(self):
        """Select backup folder."""
        folder = QFileDialog.getExistingDirectory(
            self,
            "Seleccionar Carpeta para Backups",
            self.settings.get_backup_folder()
        )
        
        if folder:
            self.folder_label.setText(folder)
            self.backup_folder = folder
            self.settings.set_backup_folder(folder)
            self.settings.save()
            self._update_filename_preview()
            self.backup_btn.setEnabled(True)
            self._log(f"Carpeta de backup configurada: {folder}")
    
    def _update_filename_preview(self):
        """Update the filename preview."""
        if hasattr(self, 'backup_folder'):
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"backup_firestore_{timestamp}.db"
            self.backup_path = os.path.join(self.backup_folder, filename)
            self.filename_label.setText(filename)
    
    def _log(self, message: str):
        """Add message to log."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
    
    def _start_backup(self):
        """Start the backup process."""
        # Verify Firestore is configured
        if not self.settings.is_firestore_configured():
            QMessageBox.warning(
                self,
                "Firestore no configurado",
                "Firestore no está configurado correctamente.\n"
                "No se puede crear un backup sin una conexión a Firestore activa."
            )
            return
        
        # Ensure backup folder exists
        if not os.path.exists(self.backup_folder):
            try:
                os.makedirs(self.backup_folder)
                self._log(f"Carpeta creada: {self.backup_folder}")
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"No se pudo crear la carpeta de backup:\n{str(e)}"
                )
                return
        
        # Update filename with current timestamp
        self._update_filename_preview()
        
        # Confirm backup
        reply = QMessageBox.question(
            self,
            "Confirmar Backup",
            f"¿Crear backup de Firestore en:\n{self.backup_path}?\n\n"
            "Este proceso puede tomar varios minutos.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        # Disable UI during backup
        self.backup_btn.setEnabled(False)
        self.close_btn.setEnabled(False)
        
        try:
            # Create repositories
            self._log("Conectando a Firestore...")
            self.firestore_repo = RepositoryFactory.create_firestore(self.settings)
            
            self._log(f"Creando archivo de backup: {self.backup_path}")
            self.sqlite_repo = RepositoryFactory.create_sqlite_for_backup(self.backup_path)
            
            # Create and start worker thread
            self._log("Iniciando backup...")
            self.worker = BackupWorker(self.firestore_repo, self.sqlite_repo)
            self.worker.progress.connect(self._on_progress)
            self.worker.finished.connect(self._on_finished)
            self.worker.start()
            
        except Exception as e:
            logger.error(f"Error iniciando backup: {e}")
            self._log(f"ERROR: {str(e)}")
            QMessageBox.critical(
                self,
                "Error",
                f"No se pudo iniciar el backup:\n\n{str(e)}"
            )
            self.backup_btn.setEnabled(True)
            self.close_btn.setEnabled(True)
    
    def _on_progress(self, percentage: int, message: str):
        """Handle progress updates."""
        self.progress_bar.setValue(percentage)
        self.status_label.setText(message)
        self._log(message)
    
    def _on_finished(self, success: bool, message: str):
        """Handle backup completion."""
        self._log(message)
        self.status_label.setText(message)
        
        # Re-enable UI
        self.close_btn.setEnabled(True)
        self.backup_btn.setEnabled(True)
        
        if success:
            self.progress_bar.setValue(100)
            QMessageBox.information(
                self,
                "Backup Exitoso",
                f"El backup se completó exitosamente.\n\n"
                f"Archivo: {self.backup_path}"
            )
        else:
            QMessageBox.critical(
                self,
                "Error de Backup",
                f"El backup falló:\n\n{message}\n\n"
                "Revisa el log para más detalles."
            )
