"""
Application Settings Manager

Manages application-wide settings including data source configuration,
theme preferences, and other user preferences.
"""
import json
import os
from typing import Dict, Any, Optional
from pathlib import Path


class AppSettings:
    """
    Centralized settings manager for the application.
    
    Stores settings in a JSON file in the user's config directory.
    """
    
    DEFAULT_SETTINGS = {
        'data_source': 'sqlite',  # 'sqlite' or 'firestore'
        'sqlite_db_path': 'progain_database.db',
        'firestore_service_account': '',
        'firestore_project_id': '',
        'theme': 'default',
        'last_project_id': None,
        'window_geometry': None,
        'ui_preferences': {
            'show_statusbar': True,
            'auto_refresh': True,
            'confirm_delete': True
        }
    }
    
    def __init__(self, settings_file: str = 'app_settings.json'):
        """
        Initialize settings manager.
        
        Args:
            settings_file: Path to settings file (relative to current directory)
        """
        self.settings_file = settings_file
        self.settings = self._load_settings()
    
    def _load_settings(self) -> Dict[str, Any]:
        """Load settings from file or create default"""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    loaded = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    settings = self.DEFAULT_SETTINGS.copy()
                    settings.update(loaded)
                    return settings
            except Exception as e:
                print(f"Warning: Could not load settings: {e}")
                return self.DEFAULT_SETTINGS.copy()
        else:
            return self.DEFAULT_SETTINGS.copy()
    
    def save(self):
        """Save current settings to file"""
        try:
            with open(self.settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving settings: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """
        Get a setting value.
        
        Args:
            key: Setting key (supports dot notation for nested keys)
            default: Default value if key not found
            
        Returns:
            Setting value or default
        """
        keys = key.split('.')
        value = self.settings
        
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        
        return value
    
    def set(self, key: str, value: Any, save: bool = True):
        """
        Set a setting value.
        
        Args:
            key: Setting key (supports dot notation for nested keys)
            value: Value to set
            save: Whether to save to file immediately
        """
        keys = key.split('.')
        current = self.settings
        
        # Navigate to the parent of the target key
        for k in keys[:-1]:
            if k not in current or not isinstance(current[k], dict):
                current[k] = {}
            current = current[k]
        
        # Set the value
        current[keys[-1]] = value
        
        if save:
            self.save()
    
    def get_data_source(self) -> str:
        """Get current data source ('sqlite' or 'firestore')"""
        return self.get('data_source', 'sqlite')
    
    def set_data_source(self, source: str, save: bool = True):
        """
        Set data source.
        
        Args:
            source: 'sqlite' or 'firestore'
            save: Whether to save immediately
        """
        if source not in ['sqlite', 'firestore']:
            raise ValueError(f"Invalid data source: {source}")
        self.set('data_source', source, save)
    
    def is_using_firestore(self) -> bool:
        """Check if currently using Firestore"""
        return self.get_data_source() == 'firestore'
    
    def is_using_sqlite(self) -> bool:
        """Check if currently using SQLite"""
        return self.get_data_source() == 'sqlite'
    
    def get_sqlite_path(self) -> str:
        """Get SQLite database path"""
        return self.get('sqlite_db_path', 'progain_database.db')
    
    def set_sqlite_path(self, path: str, save: bool = True):
        """Set SQLite database path"""
        self.set('sqlite_db_path', path, save)
    
    def get_firestore_config(self) -> Dict[str, str]:
        """Get Firestore configuration"""
        return {
            'service_account': self.get('firestore_service_account', ''),
            'project_id': self.get('firestore_project_id', '')
        }
    
    def set_firestore_config(
        self,
        service_account: str,
        project_id: str,
        save: bool = True
    ):
        """Set Firestore configuration"""
        self.set('firestore_service_account', service_account, save=False)
        self.set('firestore_project_id', project_id, save=save)
    
    def reset_to_defaults(self):
        """Reset all settings to defaults"""
        self.settings = self.DEFAULT_SETTINGS.copy()
        self.save()
    
    # Alias methods for compatibility with theme manager and other components
    def get_value(self, key: str, default=None):
        """Alias for get() method for backward compatibility"""
        return self.get(key, default)
    
    def set_value(self, key: str, value, save: bool = True):
        """Alias for set() method for backward compatibility"""
        self.set(key, value, save)


# Global settings instance
_settings_instance = None


def get_app_settings() -> AppSettings:
    """Get the global settings instance"""
    global _settings_instance
    if _settings_instance is None:
        _settings_instance = AppSettings()
    return _settings_instance
