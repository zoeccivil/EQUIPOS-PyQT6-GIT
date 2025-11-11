import os
import json
import shutil
import logging
import sys
from datetime import datetime
from typing import Optional, Dict, List
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QFileDialog, QProgressBar, QTextEdit, QCheckBox, QGroupBox,
    QMessageBox, QLineEdit, QScrollArea, QWidget
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont

# Add parent directory to path to import FirebaseMigrator
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))))

from app.migration.firebase_migrator import FirebaseMigrator


logger = logging.getLogger(__name__)


class MigrationWorker(QThread):
    """
    Worker thread for performing the actual migration.
    Emits signals to update the UI.
    """
    progress = pyqtSignal(str, int)  # message, percentage
    finished = pyqtSignal(bool, str)  # success, message
    log = pyqtSignal(str)  # log message
    
    def __init__(self, config: Dict, dry_run: bool = False):
        super().__init__()
        self.config = config
        self.dry_run = dry_run
        self.should_stop = False
        
    def run(self):
        """Execute the migration process"""
        migrator = None
        try:
            self.log.emit(f"{'DRY RUN: ' if self.dry_run else ''}Migration started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Initialize migrator
            db_path = self.config.get('db_path')
            service_account_path = self.config.get('service_account_path')
            tables = self.config.get('tables', [])
            
            self.log.emit(f"Initializing migrator...")
            self.log.emit(f"  Database: {db_path}")
            self.log.emit(f"  Service Account: {service_account_path}")
            self.log.emit(f"  Tables: {', '.join(tables)}")
            
            migrator = FirebaseMigrator(db_path, service_account_path, self.dry_run)
            
            # Initialize connections
            if not migrator.initialize_sqlite():
                self.finished.emit(False, "Failed to initialize SQLite connection")
                return
            
            if not migrator.initialize_firebase():
                self.finished.emit(False, "Failed to initialize Firebase connection")
                return
            
            # Forward migrator logs to UI
            for log_msg in migrator.migration_log:
                self.log.emit(log_msg)
            
            # Migrate tables
            total_tables = len(tables)
            
            for i, table in enumerate(tables):
                if self.should_stop:
                    self.log.emit("Migration cancelled by user")
                    self.finished.emit(False, "Migration cancelled")
                    return
                
                percentage = int((i / total_tables) * 100)
                self.progress.emit(f"Migrating table: {table}", percentage)
                
                # Perform migration
                migrated, skipped, errors = migrator.migrate_table(table)
                
                # Forward new logs
                for log_msg in migrator.migration_log[-10:]:  # Last 10 log entries
                    if log_msg not in getattr(self, '_logged_messages', set()):
                        self.log.emit(log_msg)
                        if not hasattr(self, '_logged_messages'):
                            self._logged_messages = set()
                        self._logged_messages.add(log_msg)
            
            # Handle attachments if transacciones table was migrated
            if 'transacciones' in tables or 'equipos_alquiler_meta' in tables:
                self.log.emit("Checking for attachments...")
                attachments_uploaded = migrator.migrate_attachments(
                    'transacciones',
                    'conduce_adjunto_path'
                )
                self.log.emit(f"Attachments uploaded: {attachments_uploaded}")
            
            # Save migration artifacts
            self.progress.emit("Saving migration artifacts...", 95)
            
            if not self.dry_run:
                migrator.save_mapping()
                self.log.emit("✓ ID mapping saved to mapping.json")
            
            migrator.save_log()
            self.log.emit("✓ Migration log saved to migration_log.txt")
            
            migrator.save_summary()
            self.log.emit("✓ Summary saved to migration_summary.json")
            
            # Complete
            self.progress.emit("Migration completed!", 100)
            
            # Build summary message
            stats = migrator.stats
            summary_lines = [
                f"{'Dry run' if self.dry_run else 'Migration'} completed successfully!",
                "",
                f"Total records: {stats['total_records']}",
                f"Migrated: {stats['migrated']}",
                f"Skipped (duplicates): {stats['skipped']}",
                f"Errors: {stats['errors']}"
            ]
            summary_msg = "\n".join(summary_lines)
            
            self.log.emit("")
            self.log.emit("=" * 50)
            for line in summary_lines:
                self.log.emit(line)
            self.log.emit("=" * 50)
            
            self.finished.emit(True, summary_msg)
            
        except Exception as e:
            error_msg = f"Migration error: {str(e)}"
            logger.exception(error_msg)
            self.log.emit(f"ERROR: {error_msg}")
            self.finished.emit(False, error_msg)
        finally:
            if migrator:
                migrator.close()
            logger.exception(error_msg)
            self.log.emit(f"ERROR: {error_msg}")
            self.finished.emit(False, error_msg)
    
    def stop(self):
        """Request the worker to stop"""
        self.should_stop = True


class DialogoMigracionFirebase(QDialog):
    """
    Dialog for managing Firebase migration.
    
    Features:
    - Select SQLite database file
    - Select Firebase service account credentials (external to repo)
    - Choose tables to migrate
    - Dry-run mode (count records, detect conflicts)
    - Progress tracking
    - Automatic backup creation
    - Migration logs
    """
    
    def __init__(self, db_manager=None, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.worker = None
        
        self.setWindowTitle("Migración a Firebase")
        self.resize(800, 600)
        
        self._init_ui()
        self._load_default_config()
        
    def _init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        
        # === Configuration Section ===
        config_group = QGroupBox("Configuración")
        config_layout = QVBoxLayout()
        
        # Database file selector
        db_layout = QHBoxLayout()
        db_layout.addWidget(QLabel("Base de datos SQLite:"))
        self.db_path_edit = QLineEdit()
        self.db_path_edit.setPlaceholderText("Seleccionar archivo .db")
        self.db_path_edit.setReadOnly(True)
        db_layout.addWidget(self.db_path_edit)
        btn_select_db = QPushButton("Seleccionar...")
        btn_select_db.clicked.connect(self._select_database)
        db_layout.addWidget(btn_select_db)
        config_layout.addLayout(db_layout)
        
        # Service account file selector
        sa_layout = QHBoxLayout()
        sa_layout.addWidget(QLabel("Credenciales Firebase:"))
        self.sa_path_edit = QLineEdit()
        self.sa_path_edit.setPlaceholderText("serviceAccount.json (no incluir en repo)")
        self.sa_path_edit.setReadOnly(True)
        sa_layout.addWidget(self.sa_path_edit)
        btn_select_sa = QPushButton("Seleccionar...")
        btn_select_sa.clicked.connect(self._select_service_account)
        sa_layout.addWidget(btn_select_sa)
        config_layout.addLayout(sa_layout)
        
        # Warning about credentials
        warning = QLabel("⚠️ IMPORTANTE: Las credenciales NO se subirán al repositorio (.gitignore)")
        warning.setStyleSheet("color: orange; font-weight: bold;")
        config_layout.addWidget(warning)
        
        config_group.setLayout(config_layout)
        layout.addWidget(config_group)
        
        # === Tables Selection ===
        tables_group = QGroupBox("Tablas a Migrar")
        tables_layout = QVBoxLayout()
        
        # Scroll area for checkboxes
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        
        self.table_checkboxes = {}
        tables = [
            'proyectos', 'cuentas', 'categorias', 'equipos', 'transacciones',
            'equipos_entidades', 'equipos_alquiler_meta', 'pagos', 'mantenimientos'
        ]
        
        for table in tables:
            cb = QCheckBox(table)
            cb.setChecked(True)
            self.table_checkboxes[table] = cb
            scroll_layout.addWidget(cb)
        
        scroll_layout.addStretch()
        scroll.setWidget(scroll_widget)
        tables_layout.addWidget(scroll)
        
        # Select all/none buttons
        btn_layout = QHBoxLayout()
        btn_select_all = QPushButton("Seleccionar Todo")
        btn_select_all.clicked.connect(self._select_all_tables)
        btn_select_none = QPushButton("Deseleccionar Todo")
        btn_select_none.clicked.connect(self._deselect_all_tables)
        btn_layout.addWidget(btn_select_all)
        btn_layout.addWidget(btn_select_none)
        btn_layout.addStretch()
        tables_layout.addLayout(btn_layout)
        
        tables_group.setLayout(tables_layout)
        layout.addWidget(tables_group)
        
        # === Options ===
        options_group = QGroupBox("Opciones")
        options_layout = QVBoxLayout()
        
        self.cb_dry_run = QCheckBox("Dry Run (solo contar registros y detectar conflictos)")
        self.cb_dry_run.setChecked(True)
        options_layout.addWidget(self.cb_dry_run)
        
        self.cb_backup = QCheckBox("Crear backup automático antes de migrar")
        self.cb_backup.setChecked(True)
        options_layout.addWidget(self.cb_backup)
        
        options_group.setLayout(options_layout)
        layout.addWidget(options_group)
        
        # === Progress ===
        progress_group = QGroupBox("Progreso")
        progress_layout = QVBoxLayout()
        
        self.progress_label = QLabel("Listo para comenzar")
        progress_layout.addWidget(self.progress_label)
        
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        progress_layout.addWidget(self.progress_bar)
        
        progress_group.setLayout(progress_layout)
        layout.addWidget(progress_group)
        
        # === Logs ===
        logs_group = QGroupBox("Logs")
        logs_layout = QVBoxLayout()
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Courier", 9))
        self.log_text.setMaximumHeight(150)
        logs_layout.addWidget(self.log_text)
        
        logs_group.setLayout(logs_layout)
        layout.addWidget(logs_group)
        
        # === Action Buttons ===
        btn_layout = QHBoxLayout()
        
        self.btn_start = QPushButton("Iniciar Migración")
        self.btn_start.clicked.connect(self._start_migration)
        self.btn_start.setStyleSheet("font-weight: bold;")
        btn_layout.addWidget(self.btn_start)
        
        self.btn_abort = QPushButton("Abortar")
        self.btn_abort.clicked.connect(self._abort_migration)
        self.btn_abort.setEnabled(False)
        btn_layout.addWidget(self.btn_abort)
        
        btn_layout.addStretch()
        
        btn_close = QPushButton("Cerrar")
        btn_close.clicked.connect(self.accept)
        btn_layout.addWidget(btn_close)
        
        layout.addLayout(btn_layout)
    
    def _load_default_config(self):
        """Load default configuration"""
        # Try to load existing database path if available
        if self.db_manager:
            db_path = getattr(self.db_manager, 'db_path', '')
            if db_path and os.path.exists(db_path):
                self.db_path_edit.setText(db_path)
                self._log(f"Base de datos cargada: {db_path}")
    
    def _select_database(self):
        """Select SQLite database file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar Base de Datos SQLite",
            "",
            "SQLite Database (*.db);;All Files (*)"
        )
        if file_path:
            self.db_path_edit.setText(file_path)
            self._log(f"Base de datos seleccionada: {file_path}")
    
    def _select_service_account(self):
        """Select Firebase service account JSON file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar Credenciales de Firebase",
            "",
            "JSON Files (*.json);;All Files (*)"
        )
        if file_path:
            self.sa_path_edit.setText(file_path)
            self._log(f"Credenciales seleccionadas: {file_path}")
            
            # Verify it's a valid service account file
            try:
                with open(file_path, 'r') as f:
                    data = json.load(f)
                    if 'project_id' in data and 'private_key' in data:
                        self._log(f"✓ Credenciales válidas - Proyecto: {data.get('project_id')}")
                    else:
                        self._log("⚠️ Advertencia: El archivo no parece ser un serviceAccount.json válido")
            except Exception as e:
                self._log(f"⚠️ Error al verificar credenciales: {str(e)}")
    
    def _select_all_tables(self):
        """Select all tables"""
        for cb in self.table_checkboxes.values():
            cb.setChecked(True)
        self._log("Todas las tablas seleccionadas")
    
    def _deselect_all_tables(self):
        """Deselect all tables"""
        for cb in self.table_checkboxes.values():
            cb.setChecked(False)
        self._log("Todas las tablas deseleccionadas")
    
    def _log(self, message: str):
        """Add message to log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.log_text.append(f"[{timestamp}] {message}")
        logger.info(message)
    
    def _validate_config(self) -> bool:
        """Validate configuration before starting migration"""
        if not self.db_path_edit.text():
            QMessageBox.warning(self, "Error", "Selecciona una base de datos SQLite")
            return False
        
        if not os.path.exists(self.db_path_edit.text()):
            QMessageBox.warning(self, "Error", "El archivo de base de datos no existe")
            return False
        
        if not self.sa_path_edit.text():
            QMessageBox.warning(self, "Error", "Selecciona el archivo de credenciales de Firebase")
            return False
        
        if not os.path.exists(self.sa_path_edit.text()):
            QMessageBox.warning(self, "Error", "El archivo de credenciales no existe")
            return False
        
        selected_tables = [name for name, cb in self.table_checkboxes.items() if cb.isChecked()]
        if not selected_tables:
            QMessageBox.warning(self, "Error", "Selecciona al menos una tabla para migrar")
            return False
        
        return True
    
    def _create_backup(self) -> Optional[str]:
        """Create backup of the database"""
        try:
            db_path = self.db_path_edit.text()
            backup_dir = "backups"
            os.makedirs(backup_dir, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"backup_{os.path.basename(db_path)}_{timestamp}"
            backup_path = os.path.join(backup_dir, backup_filename)
            
            shutil.copy2(db_path, backup_path)
            self._log(f"✓ Backup creado: {backup_path}")
            
            return backup_path
        except Exception as e:
            self._log(f"✗ Error al crear backup: {str(e)}")
            return None
    
    def _start_migration(self):
        """Start the migration process"""
        if not self._validate_config():
            return
        
        # Create backup if requested
        if self.cb_backup.isChecked() and not self.cb_dry_run.isChecked():
            if not self._create_backup():
                reply = QMessageBox.question(
                    self,
                    "Backup Failed",
                    "No se pudo crear el backup. ¿Continuar de todos modos?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.No:
                    return
        
        # Prepare configuration
        selected_tables = [name for name, cb in self.table_checkboxes.items() if cb.isChecked()]
        config = {
            'db_path': self.db_path_edit.text(),
            'service_account_path': self.sa_path_edit.text(),
            'tables': selected_tables
        }
        
        # Disable UI elements
        self.btn_start.setEnabled(False)
        self.btn_abort.setEnabled(True)
        for cb in self.table_checkboxes.values():
            cb.setEnabled(False)
        self.cb_dry_run.setEnabled(False)
        self.cb_backup.setEnabled(False)
        
        # Start worker thread
        self.worker = MigrationWorker(config, self.cb_dry_run.isChecked())
        self.worker.progress.connect(self._on_progress)
        self.worker.log.connect(self._log)
        self.worker.finished.connect(self._on_finished)
        self.worker.start()
        
        self._log("=" * 50)
        self._log(f"Iniciando {'dry run' if self.cb_dry_run.isChecked() else 'migración'}")
        self._log(f"Tablas: {', '.join(selected_tables)}")
    
    def _abort_migration(self):
        """Abort the migration process"""
        if self.worker and self.worker.isRunning():
            reply = QMessageBox.question(
                self,
                "Confirmar Abortar",
                "¿Estás seguro de que quieres abortar la migración?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            if reply == QMessageBox.StandardButton.Yes:
                self.worker.stop()
                self._log("Abortando migración...")
    
    def _on_progress(self, message: str, percentage: int):
        """Handle progress update"""
        self.progress_label.setText(message)
        self.progress_bar.setValue(percentage)
    
    def _on_finished(self, success: bool, message: str):
        """Handle migration completion"""
        # Re-enable UI elements
        self.btn_start.setEnabled(True)
        self.btn_abort.setEnabled(False)
        for cb in self.table_checkboxes.values():
            cb.setEnabled(True)
        self.cb_dry_run.setEnabled(True)
        self.cb_backup.setEnabled(True)
        
        if success:
            QMessageBox.information(self, "Éxito", message)
        else:
            QMessageBox.warning(self, "Error", message)
        
        self._log("=" * 50)
