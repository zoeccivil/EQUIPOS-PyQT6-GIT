"""
Data Source Toggle Widget

Provides a widget to switch between SQLite and Firestore data sources.
Shows current data source and allows configuration of each source.
"""
import os
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QButtonGroup, QRadioButton, QGroupBox, QLineEdit, QFileDialog,
    QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont


class DataSourceWidget(QWidget):
    """
    Widget for selecting and configuring data source (SQLite or Firestore).
    
    Signals:
        data_source_changed: Emitted when data source changes (new_source: str)
    """
    
    data_source_changed = pyqtSignal(str)  # 'sqlite' or 'firestore'
    
    def __init__(self, settings, parent=None):
        super().__init__(parent)
        self.settings = settings
        self._init_ui()
        self._load_current_settings()
    
    def _init_ui(self):
        """Initialize the user interface"""
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Fuente de Datos")
        title_font = QFont()
        title_font.setBold(True)
        title_font.setPointSize(12)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Current status indicator
        self.status_label = QLabel()
        self.status_label.setStyleSheet("""
            QLabel {
                padding: 8px;
                border-radius: 4px;
                background-color: #e3f2fd;
                color: #1976d2;
            }
        """)
        layout.addWidget(self.status_label)
        
        # Radio buttons for source selection
        source_group = QGroupBox("Seleccionar Fuente")
        source_layout = QVBoxLayout()
        
        self.sqlite_radio = QRadioButton("SQLite (Base de datos local)")
        self.firestore_radio = QRadioButton("Firebase Firestore (Nube)")
        
        self.button_group = QButtonGroup()
        self.button_group.addButton(self.sqlite_radio)
        self.button_group.addButton(self.firestore_radio)
        
        source_layout.addWidget(self.sqlite_radio)
        source_layout.addWidget(self.firestore_radio)
        source_group.setLayout(source_layout)
        layout.addWidget(source_group)
        
        # SQLite configuration
        self.sqlite_config = self._create_sqlite_config()
        layout.addWidget(self.sqlite_config)
        
        # Firestore configuration
        self.firestore_config = self._create_firestore_config()
        layout.addWidget(self.firestore_config)
        
        # Apply button
        apply_btn = QPushButton("Aplicar y Reiniciar")
        apply_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px;
                border: none;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        apply_btn.clicked.connect(self._apply_settings)
        layout.addWidget(apply_btn)
        
        layout.addStretch()
        
        # Connect signals
        self.sqlite_radio.toggled.connect(self._update_config_visibility)
        self.firestore_radio.toggled.connect(self._update_config_visibility)
    
    def _create_sqlite_config(self) -> QGroupBox:
        """Create SQLite configuration group"""
        group = QGroupBox("Configuración SQLite")
        layout = QVBoxLayout()
        
        # Database path
        path_layout = QHBoxLayout()
        path_layout.addWidget(QLabel("Ruta de la BD:"))
        self.sqlite_path_input = QLineEdit()
        self.sqlite_path_input.setPlaceholderText("progain_database.db")
        path_layout.addWidget(self.sqlite_path_input)
        
        browse_btn = QPushButton("Explorar...")
        browse_btn.clicked.connect(self._browse_sqlite_file)
        path_layout.addWidget(browse_btn)
        
        layout.addLayout(path_layout)
        group.setLayout(layout)
        
        return group
    
    def _create_firestore_config(self) -> QGroupBox:
        """Create Firestore configuration group"""
        group = QGroupBox("Configuración Firebase Firestore")
        layout = QVBoxLayout()
        
        # Service account path
        sa_layout = QHBoxLayout()
        sa_layout.addWidget(QLabel("Service Account:"))
        self.firestore_sa_input = QLineEdit()
        self.firestore_sa_input.setPlaceholderText("serviceAccount.json")
        sa_layout.addWidget(self.firestore_sa_input)
        
        browse_btn = QPushButton("Explorar...")
        browse_btn.clicked.connect(self._browse_service_account)
        sa_layout.addWidget(browse_btn)
        
        layout.addLayout(sa_layout)
        
        # Project ID
        project_layout = QHBoxLayout()
        project_layout.addWidget(QLabel("Project ID:"))
        self.firestore_project_input = QLineEdit()
        self.firestore_project_input.setPlaceholderText("progain-prod")
        project_layout.addWidget(self.firestore_project_input)
        
        layout.addLayout(project_layout)
        
        # Warning
        warning = QLabel("⚠️ Asegúrese de que las credenciales de Firebase estén configuradas correctamente")
        warning.setWordWrap(True)
        warning.setStyleSheet("color: #ff9800; padding: 5px;")
        layout.addWidget(warning)
        
        group.setLayout(layout)
        
        return group
    
    def _browse_sqlite_file(self):
        """Browse for SQLite database file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar Base de Datos SQLite",
            "",
            "SQLite Database (*.db *.sqlite);;All Files (*)"
        )
        if file_path:
            self.sqlite_path_input.setText(file_path)
    
    def _browse_service_account(self):
        """Browse for Firebase service account JSON"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar Service Account JSON",
            "",
            "JSON Files (*.json);;All Files (*)"
        )
        if file_path:
            self.firestore_sa_input.setText(file_path)
    
    def _load_current_settings(self):
        """Load current settings from AppSettings"""
        # Set current data source
        current_source = self.settings.get_data_source()
        if current_source == 'sqlite':
            self.sqlite_radio.setChecked(True)
        else:
            self.firestore_radio.setChecked(True)
        
        # Load SQLite path
        sqlite_path = self.settings.get_sqlite_path()
        self.sqlite_path_input.setText(sqlite_path)
        
        # Load Firestore config
        firestore_config = self.settings.get_firestore_config()
        self.firestore_sa_input.setText(firestore_config.get('service_account', ''))
        self.firestore_project_input.setText(firestore_config.get('project_id', ''))
        
        # Update UI
        self._update_config_visibility()
        self._update_status_label()
    
    def _update_config_visibility(self):
        """Show/hide configuration groups based on selection"""
        is_sqlite = self.sqlite_radio.isChecked()
        self.sqlite_config.setVisible(is_sqlite)
        self.firestore_config.setVisible(not is_sqlite)
    
    def _update_status_label(self):
        """Update the status label to show current source"""
        current_source = self.settings.get_data_source()
        if current_source == 'sqlite':
            db_path = self.settings.get_sqlite_path()
            self.status_label.setText(f"🗄️ Usando SQLite: {db_path}")
            self.status_label.setStyleSheet("""
                QLabel {
                    padding: 8px;
                    border-radius: 4px;
                    background-color: #e3f2fd;
                    color: #1976d2;
                }
            """)
        else:
            config = self.settings.get_firestore_config()
            project_id = config.get('project_id', 'No configurado')
            self.status_label.setText(f"☁️ Usando Firestore: {project_id}")
            self.status_label.setStyleSheet("""
                QLabel {
                    padding: 8px;
                    border-radius: 4px;
                    background-color: #fff3e0;
                    color: #f57c00;
                }
            """)
    
    def _apply_settings(self):
        """Apply and save settings"""
        # Determine which source is selected
        new_source = 'sqlite' if self.sqlite_radio.isChecked() else 'firestore'
        
        # Validate inputs
        if new_source == 'sqlite':
            db_path = self.sqlite_path_input.text().strip()
            if not db_path:
                QMessageBox.warning(
                    self,
                    "Error de Configuración",
                    "Por favor especifique la ruta de la base de datos SQLite"
                )
                return
            
            # Save SQLite settings
            self.settings.set_sqlite_path(db_path, save=False)
            
        else:  # firestore
            sa_path = self.firestore_sa_input.text().strip()
            project_id = self.firestore_project_input.text().strip()
            
            if not sa_path or not project_id:
                QMessageBox.warning(
                    self,
                    "Error de Configuración",
                    "Por favor especifique tanto el Service Account como el Project ID"
                )
                return
            
            if not os.path.exists(sa_path):
                QMessageBox.warning(
                    self,
                    "Archivo No Encontrado",
                    f"No se encontró el archivo de Service Account:\n{sa_path}"
                )
                return
            
            # Save Firestore settings
            self.settings.set_firestore_config(sa_path, project_id, save=False)
        
        # Save data source selection
        self.settings.set_data_source(new_source, save=True)
        
        # Update status
        self._update_status_label()
        
        # Emit signal
        self.data_source_changed.emit(new_source)
        
        # Show restart message
        QMessageBox.information(
            self,
            "Configuración Guardada",
            f"La fuente de datos se ha cambiado a {new_source.upper()}.\n\n"
            "Por favor reinicie la aplicación para que los cambios surtan efecto."
        )
    
    def get_current_source(self) -> str:
        """Get currently selected source"""
        return 'sqlite' if self.sqlite_radio.isChecked() else 'firestore'
