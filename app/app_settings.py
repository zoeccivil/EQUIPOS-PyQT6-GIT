"""
Centralized application settings management.

Manages configuration for:
- Data source selection (Firestore vs SQLite)
- Firestore authentication (email/password)
- Backup locations
"""
import json
import os
from typing import Optional, Dict, Any

# Configuration file path
SETTINGS_FILE = 'app_settings.json'

# Default settings structure
DEFAULT_SETTINGS = {
    "data_source": "firestore",  # "firestore" or "sqlite"
    "firestore": {
        "project_id": "",
        "email": "",
        "password": "",
        "api_key": ""  # For web API authentication
    },
    "sqlite": {
        "database_path": "progain_database.db"
    },
    "backup": {
        "sqlite_folder": "./backups"
    },
    "migration": {
        "last_migration_date": None,
        "sqlite_source_path": None
    },
    # Legacy config for backward compatibility
    "database_path": "progain_database.db",
    "carpeta_conduces": ""
}


class AppSettings:
    """Manages application settings with validation."""
    
    def __init__(self, settings_file: str = SETTINGS_FILE):
        self.settings_file = settings_file
        self._settings = self._load_settings()
    
    def _load_settings(self) -> Dict[str, Any]:
        """Load settings from file, creating defaults if not exists."""
        if not os.path.exists(self.settings_file):
            self._settings = DEFAULT_SETTINGS.copy()
            self.save()
            return self._settings
        
        try:
            with open(self.settings_file, 'r', encoding='utf-8') as f:
                loaded = json.load(f)
            # Merge with defaults to ensure all keys exist
            settings = DEFAULT_SETTINGS.copy()
            self._deep_update(settings, loaded)
            return settings
        except Exception as e:
            print(f"Error loading settings: {e}. Using defaults.")
            return DEFAULT_SETTINGS.copy()
    
    def _deep_update(self, base: dict, updates: dict) -> None:
        """Deep update base dict with updates dict."""
        for key, value in updates.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_update(base[key], value)
            else:
                base[key] = value
    
    def save(self) -> bool:
        """Save current settings to file."""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self._settings, f, indent=4, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False
    
    def get(self, key_path: str, default: Any = None) -> Any:
        """
        Get a setting value using dot notation.
        Example: get("firestore.project_id")
        """
        keys = key_path.split('.')
        value = self._settings
        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default
        return value
    
    def set(self, key_path: str, value: Any) -> None:
        """
        Set a setting value using dot notation.
        Example: set("firestore.project_id", "my-project")
        """
        keys = key_path.split('.')
        current = self._settings
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]
        current[keys[-1]] = value
    
    def get_data_source(self) -> str:
        """Get the configured data source ('firestore' or 'sqlite')."""
        return self.get("data_source", "firestore")
    
    def set_data_source(self, source: str) -> None:
        """Set the data source ('firestore' or 'sqlite')."""
        if source not in ["firestore", "sqlite"]:
            raise ValueError(f"Invalid data source: {source}")
        self.set("data_source", source)
    
    def is_firestore_configured(self) -> bool:
        """Check if Firestore is properly configured."""
        project_id = self.get("firestore.project_id", "")
        email = self.get("firestore.email", "")
        password = self.get("firestore.password", "")
        api_key = self.get("firestore.api_key", "")
        
        return bool(project_id and email and password and api_key)
    
    def get_firestore_config(self) -> Dict[str, str]:
        """Get Firestore configuration."""
        return {
            "project_id": self.get("firestore.project_id", ""),
            "email": self.get("firestore.email", ""),
            "password": self.get("firestore.password", ""),
            "api_key": self.get("firestore.api_key", "")
        }
    
    def set_firestore_config(self, project_id: str, email: str, password: str, api_key: str) -> None:
        """Set Firestore configuration."""
        self.set("firestore.project_id", project_id)
        self.set("firestore.email", email)
        self.set("firestore.password", password)
        self.set("firestore.api_key", api_key)
    
    def get_backup_folder(self) -> str:
        """Get the configured backup folder path."""
        return self.get("backup.sqlite_folder", "./backups")
    
    def set_backup_folder(self, folder: str) -> None:
        """Set the backup folder path."""
        self.set("backup.sqlite_folder", folder)
    
    def get_sqlite_path(self) -> str:
        """Get the SQLite database path."""
        return self.get("sqlite.database_path", "progain_database.db")
    
    def set_sqlite_path(self, path: str) -> None:
        """Set the SQLite database path."""
        self.set("sqlite.database_path", path)
        # Also update legacy key for backward compatibility
        self.set("database_path", path)


# Global settings instance
_settings_instance: Optional[AppSettings] = None


def get_settings() -> AppSettings:
    """Get or create the global settings instance."""
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = AppSettings()
    return _settings_instance


def save_settings() -> bool:
    """Save the global settings instance."""
    return get_settings().save()
