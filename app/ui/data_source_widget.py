"""
Data source configuration widget.

UI for configuring Firestore authentication and data source selection.
"""
import logging
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, 
    QPushButton, QMessageBox, QGroupBox, QFormLayout, QComboBox
)
from PyQt6.QtCore import Qt

from app.app_settings import AppSettings, get_settings

logger = logging.getLogger(__name__)


class DataSourceWidget(QDialog):
    """
    Dialog for configuring data source (Firestore or SQLite).
    
    Allows users to:
    - Select data source (Firestore or SQLite)
    - Configure Firestore authentication (email/password)
    - Test Firestore connection
    """
    
    def __init__(self, parent=None, settings: AppSettings = None):
        super().__init__(parent)
        self.settings = settings or get_settings()
        self.setWindowTitle("Configuración de Fuente de Datos")
        self.setModal(True)
        self.resize(500, 400)
        
        self._init_ui()
        self._load_current_settings()
    
    def _init_ui(self):
        """Initialize the user interface."""
        layout = QVBoxLayout()
        
        # Data source selection
        source_group = QGroupBox("Fuente de Datos Principal")
        source_layout = QFormLayout()
        
        self.source_combo = QComboBox()
        self.source_combo.addItems(["Firestore", "SQLite"])
        self.source_combo.currentTextChanged.connect(self._on_source_changed)
        source_layout.addRow("Fuente de datos:", self.source_combo)
        
        source_group.setLayout(source_layout)
        layout.addWidget(source_group)
        
        # Firestore configuration group
        self.firestore_group = QGroupBox("Configuración de Firestore")
        firestore_layout = QFormLayout()
        
        self.project_id_input = QLineEdit()
        self.project_id_input.setPlaceholderText("mi-proyecto-firebase")
        firestore_layout.addRow("Project ID:", self.project_id_input)
        
        self.api_key_input = QLineEdit()
        self.api_key_input.setPlaceholderText("AIza...")
        firestore_layout.addRow("API Key:", self.api_key_input)
        
        self.email_input = QLineEdit()
        self.email_input.setPlaceholderText("usuario@example.com")
        firestore_layout.addRow("Email:", self.email_input)
        
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("••••••••")
        firestore_layout.addRow("Contraseña:", self.password_input)
        
        # Test connection button
        test_btn_layout = QHBoxLayout()
        self.test_btn = QPushButton("Probar Conexión")
        self.test_btn.clicked.connect(self._test_firestore_connection)
        test_btn_layout.addStretch()
        test_btn_layout.addWidget(self.test_btn)
        firestore_layout.addRow("", test_btn_layout)
        
        self.firestore_group.setLayout(firestore_layout)
        layout.addWidget(self.firestore_group)
        
        # Help text
        help_label = QLabel(
            "<b>Cómo obtener las credenciales de Firestore:</b><br>"
            "1. Ve a la consola de Firebase: <a href='https://console.firebase.google.com'>console.firebase.google.com</a><br>"
            "2. Selecciona tu proyecto<br>"
            "3. En 'Project Settings', copia el 'Project ID' y 'Web API Key'<br>"
            "4. En 'Authentication', habilita 'Email/Password' y crea un usuario<br>"
            "5. Usa las credenciales del usuario creado en los campos de arriba"
        )
        help_label.setWordWrap(True)
        help_label.setOpenExternalLinks(True)
        help_label.setStyleSheet("color: #666; font-size: 10px; padding: 10px;")
        layout.addWidget(help_label)
        
        layout.addStretch()
        
        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()
        
        save_btn = QPushButton("Guardar")
        save_btn.clicked.connect(self._save_settings)
        btn_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("Cancelar")
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
        
        self.setLayout(layout)
    
    def _load_current_settings(self):
        """Load current settings into the form."""
        # Data source
        current_source = self.settings.get_data_source()
        if current_source == "firestore":
            self.source_combo.setCurrentText("Firestore")
        else:
            self.source_combo.setCurrentText("SQLite")
        
        # Firestore config
        firestore_config = self.settings.get_firestore_config()
        self.project_id_input.setText(firestore_config.get("project_id", ""))
        self.api_key_input.setText(firestore_config.get("api_key", ""))
        self.email_input.setText(firestore_config.get("email", ""))
        self.password_input.setText(firestore_config.get("password", ""))
        
        self._on_source_changed(self.source_combo.currentText())
    
    def _on_source_changed(self, source: str):
        """Handle data source selection change."""
        # Enable/disable Firestore group based on selection
        self.firestore_group.setEnabled(source == "Firestore")
    
    def _test_firestore_connection(self):
        """Test Firestore connection with current settings."""
        project_id = self.project_id_input.text().strip()
        api_key = self.api_key_input.text().strip()
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()
        
        if not all([project_id, api_key, email, password]):
            QMessageBox.warning(
                self,
                "Campos incompletos",
                "Por favor completa todos los campos de configuración de Firestore."
            )
            return
        
        # Show progress
        self.test_btn.setEnabled(False)
        self.test_btn.setText("Probando...")
        
        try:
            from app.repo.firestore_repository import FirestoreRepository
            
            # Try to create and authenticate
            repo = FirestoreRepository(
                project_id=project_id,
                email=email,
                password=password,
                api_key=api_key
            )
            
            # Test connection
            if repo.verificar_conexion():
                QMessageBox.information(
                    self,
                    "Conexión exitosa",
                    "La conexión a Firestore se estableció correctamente."
                )
            else:
                QMessageBox.warning(
                    self,
                    "Conexión fallida",
                    "No se pudo verificar la conexión a Firestore."
                )
            
            repo.cerrar()
            
        except Exception as e:
            logger.error(f"Error probando conexión Firestore: {e}")
            QMessageBox.critical(
                self,
                "Error de conexión",
                f"No se pudo conectar a Firestore:\n\n{str(e)}\n\n"
                "Verifica tus credenciales e intenta nuevamente."
            )
        finally:
            self.test_btn.setEnabled(True)
            self.test_btn.setText("Probar Conexión")
    
    def _save_settings(self):
        """Save the current settings."""
        # Get selected source
        source = "firestore" if self.source_combo.currentText() == "Firestore" else "sqlite"
        
        # If Firestore is selected, validate configuration
        if source == "firestore":
            project_id = self.project_id_input.text().strip()
            api_key = self.api_key_input.text().strip()
            email = self.email_input.text().strip()
            password = self.password_input.text().strip()
            
            if not all([project_id, api_key, email, password]):
                QMessageBox.warning(
                    self,
                    "Configuración incompleta",
                    "Por favor completa todos los campos de Firestore antes de guardar."
                )
                return
            
            # Save Firestore config
            self.settings.set_firestore_config(
                project_id=project_id,
                email=email,
                password=password,
                api_key=api_key
            )
        
        # Save data source selection
        self.settings.set_data_source(source)
        
        # Persist settings
        if self.settings.save():
            QMessageBox.information(
                self,
                "Configuración guardada",
                "La configuración se ha guardado correctamente.\n\n"
                "Reinicia la aplicación para que los cambios tengan efecto."
            )
            self.accept()
        else:
            QMessageBox.critical(
                self,
                "Error",
                "No se pudo guardar la configuración. Revisa los permisos del archivo."
            )
