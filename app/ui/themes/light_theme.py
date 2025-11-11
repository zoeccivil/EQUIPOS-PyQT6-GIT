"""
Light Theme for PROGAIN PyQt6 application.

Classic clean light theme
"""

THEME_STYLESHEET = """
QMainWindow {
    background-color: #ffffff;
    color: #000000;
}

QWidget {
    background-color: #ffffff;
    color: #000000;
}

QPushButton {
    background-color: #f0f0f0;
    color: #000000;
    border: 1px solid #0078d4;
    padding: 5px 15px;
    border-radius: 3px;
}

QPushButton:hover {
    background-color: #0078d4;
    color: #ffffff;
}

QPushButton:pressed {
    background-color: #cce8ff;
}

QTableWidget {
    background-color: #ffffff;
    alternate-background-color: #f0f0f0;
    color: #000000;
    gridline-color: #f0f0f0;
    selection-background-color: #cce8ff;
}

QTableWidget::item:selected {
    background-color: #cce8ff;
}

QHeaderView::section {
    background-color: #f0f0f0;
    color: #000000;
    padding: 5px;
    border: 1px solid #ffffff;
}

QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: #f0f0f0;
    color: #000000;
    border: 1px solid #0078d4;
    padding: 3px;
    border-radius: 2px;
}

QComboBox {
    background-color: #f0f0f0;
    color: #000000;
    border: 1px solid #0078d4;
    padding: 3px;
}

QMenuBar {
    background-color: #ffffff;
    color: #000000;
}

QMenuBar::item:selected {
    background-color: #0078d4;
}

QMenu {
    background-color: #f0f0f0;
    color: #000000;
    border: 1px solid #0078d4;
}

QMenu::item:selected {
    background-color: #0078d4;
}

QTabWidget::pane {
    border: 1px solid #0078d4;
}

QTabBar::tab {
    background-color: #f0f0f0;
    color: #000000;
    padding: 8px 16px;
}

QTabBar::tab:selected {
    background-color: #0078d4;
    color: #ffffff;
}

QScrollBar:vertical {
    background-color: #ffffff;
    width: 12px;
}

QScrollBar::handle:vertical {
    background-color: #0078d4;
    border-radius: 6px;
}

QStatusBar {
    background-color: #f0f0f0;
    color: #000000;
}
"""

THEME_METADATA = {
    'name': 'Light Theme',
    'description': 'Classic clean light theme',
    'author': 'PROGAIN Development Team',
    'version': '1.0',
    'type': 'light'
}
