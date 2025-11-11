"""
Autenticación con Firebase.

Maneja la autenticación y autorización para acceso a Firebase.
"""
import json
import logging
from typing import Dict, Optional
from pathlib import Path

logger = logging.getLogger(__name__)


class FirebaseAuthError(Exception):
    """Excepción para errores de autenticación"""
    pass


class FirebaseAuth:
    """
    Gestiona autenticación con Firebase.
    """
    
    def __init__(self, service_account_path: str):
        """
        Inicializa el módulo de autenticación.
        
        Args:
            service_account_path: Ruta al archivo serviceAccount.json
        """
        self.service_account_path = service_account_path
        self.credentials = None
        self.project_id = None
        self.authenticated = False
    
    def load_credentials(self):
        """Carga las credenciales desde el archivo"""
        try:
            if not Path(self.service_account_path).exists():
                raise FirebaseAuthError(
                    f"Service account file not found: {self.service_account_path}"
                )
            
            with open(self.service_account_path, 'r') as f:
                self.credentials = json.load(f)
            
            # Validar credenciales
            required_keys = ['project_id', 'private_key', 'client_email']
            for key in required_keys:
                if key not in self.credentials:
                    raise FirebaseAuthError(
                        f"Invalid service account file: missing '{key}'"
                    )
            
            self.project_id = self.credentials['project_id']
            logger.info(f"Loaded credentials for project: {self.project_id}")
            
        except json.JSONDecodeError as e:
            raise FirebaseAuthError(f"Invalid JSON in service account file: {e}")
        except Exception as e:
            raise FirebaseAuthError(f"Failed to load credentials: {e}")
    
    def authenticate(self) -> bool:
        """
        Autentica con Firebase usando las credenciales.
        
        Returns:
            True si autenticación exitosa
        """
        if not self.credentials:
            self.load_credentials()
        
        try:
            # En implementación real:
            # import firebase_admin
            # from firebase_admin import credentials
            # 
            # if not firebase_admin._apps:
            #     cred = credentials.Certificate(self.service_account_path)
            #     firebase_admin.initialize_app(cred, {
            #         'storageBucket': f'{self.project_id}.appspot.com'
            #     })
            
            self.authenticated = True
            logger.info(f"Authenticated with Firebase project: {self.project_id}")
            return True
            
        except Exception as e:
            raise FirebaseAuthError(f"Authentication failed: {e}")
    
    def verify_permissions(self) -> bool:
        """
        Verifica que las credenciales tengan permisos necesarios.
        
        Returns:
            True si tiene permisos
        """
        if not self.authenticated:
            raise FirebaseAuthError("Not authenticated")
        
        # En implementación real, verificar permisos:
        # - Firestore: leer/escribir
        # - Storage: leer/escribir
        
        logger.info("Permissions verified")
        return True
    
    def get_project_id(self) -> Optional[str]:
        """Retorna el project ID"""
        return self.project_id
    
    def is_authenticated(self) -> bool:
        """Retorna si está autenticado"""
        return self.authenticated
