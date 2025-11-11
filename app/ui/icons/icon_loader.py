"""
Icon Loader for PROGAIN PyQt6 application.

Provides unified icon loading with multiple fallback strategies.
"""

import logging
from PyQt6.QtGui import QIcon
from PyQt6.QtWidgets import QStyle, QApplication

logger = logging.getLogger(__name__)

# Icon mapping: semantic name -> FontAwesome icon name
ICON_MAP = {
    # Actions
    'add': 'fa.plus',
    'edit': 'fa.edit',
    'delete': 'fa.trash',
    'save': 'fa.save',
    'cancel': 'fa.times',
    'ok': 'fa.check',
    'refresh': 'fa.refresh',
    'search': 'fa.search',
    'filter': 'fa.filter',
    'export': 'fa.file-export',
    'import': 'fa.file-import',
    'print': 'fa.print',
    'copy': 'fa.copy',
    'paste': 'fa.paste',
    'cut': 'fa.cut',
    'undo': 'fa.undo',
    'redo': 'fa.redo',
    
    # Settings
    'settings': 'fa.cog',
    'preferences': 'fa.sliders-h',
    'theme': 'fa.palette',
    
    # Navigation
    'back': 'fa.arrow-left',
    'forward': 'fa.arrow-right',
    'up': 'fa.arrow-up',
    'down': 'fa.arrow-down',
    'home': 'fa.home',
    
    # Files
    'file': 'fa.file',
    'folder': 'fa.folder',
    'open': 'fa.folder-open',
    'attach': 'fa.paperclip',
    
    # Data
    'database': 'fa.database',
    'cloud': 'fa.cloud',
    'download': 'fa.download',
    'upload': 'fa.upload',
    'sync': 'fa.sync',
    
    # UI Elements
    'menu': 'fa.bars',
    'more': 'fa.ellipsis-v',
    'close': 'fa.times',
    'minimize': 'fa.minus',
    'maximize': 'fa.expand',
    
    # Status
    'warning': 'fa.exclamation-triangle',
    'info': 'fa.info-circle',
    'success': 'fa.check-circle',
    'error': 'fa.times-circle',
    'question': 'fa.question-circle',
    
    # Domain Specific
    'project': 'fa.folder-open',
    'equipment': 'fa.tools',
    'user': 'fa.user',
    'users': 'fa.users',
    'client': 'fa.user-tie',
    'operator': 'fa.user-hard-hat',
    'transaction': 'fa.exchange-alt',
    'payment': 'fa.dollar-sign',
    'maintenance': 'fa.wrench',
    'calendar': 'fa.calendar',
    'chart': 'fa.chart-bar',
    'report': 'fa.file-alt',
    'location': 'fa.map-marker-alt',
    'invoice': 'fa.file-invoice',
    'contract': 'fa.file-contract',
}


def get_icon(name: str) -> QIcon:
    """
    Get icon by semantic name with fallback strategies.
    
    Args:
        name: Semantic icon name (e.g., 'add', 'delete', 'save')
    
    Returns:
        QIcon instance
    
    Fallback order:
    1. qtawesome (FontAwesome)
    2. QStyle native icons
    3. Empty QIcon
    """
    # Strategy 1: Try qtawesome
    try:
        import qtawesome as qta
        
        icon_name = ICON_MAP.get(name)
        if icon_name:
            return qta.icon(icon_name)
    except ImportError:
        pass
    except Exception as e:
        logger.debug(f"qtawesome failed for {name}: {e}")
    
    # Strategy 2: Try QStyle native icons
    app = QApplication.instance()
    if app:
        style = app.style()
        style_map = {
            'add': QStyle.StandardPixmap.SP_FileDialogNewFolder,
            'delete': QStyle.StandardPixmap.SP_TrashIcon,
            'save': QStyle.StandardPixmap.SP_DialogSaveButton,
            'open': QStyle.StandardPixmap.SP_DirOpenIcon,
            'folder': QStyle.StandardPixmap.SP_DirIcon,
            'file': QStyle.StandardPixmap.SP_FileIcon,
            'close': QStyle.StandardPixmap.SP_DialogCloseButton,
            'ok': QStyle.StandardPixmap.SP_DialogOkButton,
            'cancel': QStyle.StandardPixmap.SP_DialogCancelButton,
            'info': QStyle.StandardPixmap.SP_MessageBoxInformation,
            'warning': QStyle.StandardPixmap.SP_MessageBoxWarning,
            'error': QStyle.StandardPixmap.SP_MessageBoxCritical,
            'question': QStyle.StandardPixmap.SP_MessageBoxQuestion,
        }
        
        if name in style_map:
            return style.standardIcon(style_map[name])
    
    # Strategy 3: Return empty icon
    return QIcon()
