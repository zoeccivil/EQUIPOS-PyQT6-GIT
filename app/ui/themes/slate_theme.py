"""
Slate Theme for PROGAIN PyQt6 application.

Professional dark slate with orange accents
"""

THEME_STYLESHEET = """
QMainWindow {
    background-color: #263238;
    color: #eceff1;
}

QWidget {
    background-color: #263238;
    color: #eceff1;
}

QPushButton {
    background-color: #37474f;
    color: #eceff1;
    border: 1px solid #ff9800;
    padding: 5px 15px;
    border-radius: 3px;
}

QPushButton:hover {
    background-color: #ff9800;
    color: #263238;
}

QPushButton:pressed {
    background-color: #e65100;
}

QTableWidget {
    background-color: #263238;
    alternate-background-color: #37474f;
    color: #eceff1;
    gridline-color: #37474f;
    selection-background-color: #e65100;
}

QTableWidget::item:selected {
    background-color: #e65100;
}

QHeaderView::section {
    background-color: #37474f;
    color: #eceff1;
    padding: 5px;
    border: 1px solid #263238;
}

QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: #37474f;
    color: #eceff1;
    border: 1px solid #ff9800;
    padding: 3px;
    border-radius: 2px;
}

QComboBox {
    background-color: #37474f;
    color: #eceff1;
    border: 1px solid #ff9800;
    padding: 3px;
}

QMenuBar {
    background-color: #263238;
    color: #eceff1;
}

QMenuBar::item:selected {
    background-color: #ff9800;
}

QMenu {
    background-color: #37474f;
    color: #eceff1;
    border: 1px solid #ff9800;
}

QMenu::item:selected {
    background-color: #ff9800;
}

QTabWidget::pane {
    border: 1px solid #ff9800;
}

QTabBar::tab {
    background-color: #37474f;
    color: #eceff1;
    padding: 8px 16px;
}

QTabBar::tab:selected {
    background-color: #ff9800;
    color: #263238;
}

QScrollBar:vertical {
    background-color: #263238;
    width: 12px;
}

QScrollBar::handle:vertical {
    background-color: #ff9800;
    border-radius: 6px;
}

QStatusBar {
    background-color: #37474f;
    color: #eceff1;
}
"""

THEME_METADATA = {
    'name': 'Slate Theme',
    'description': 'Professional dark slate with orange accents',
    'author': 'PROGAIN Development Team',
    'version': '1.0',
    'type': 'dark'
}
