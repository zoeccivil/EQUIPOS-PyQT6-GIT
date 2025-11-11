"""
Charcoal Theme for PROGAIN PyQt6 application.

Modern dark theme with blue accents
"""

THEME_STYLESHEET = """
QMainWindow {
    background-color: #2b2b2b;
    color: #ffffff;
}

QWidget {
    background-color: #2b2b2b;
    color: #ffffff;
}

QPushButton {
    background-color: #3a3a3a;
    color: #ffffff;
    border: 1px solid #4a9eff;
    padding: 5px 15px;
    border-radius: 3px;
}

QPushButton:hover {
    background-color: #4a9eff;
    color: #2b2b2b;
}

QPushButton:pressed {
    background-color: #1e5a8e;
}

QTableWidget {
    background-color: #2b2b2b;
    alternate-background-color: #3a3a3a;
    color: #ffffff;
    gridline-color: #3a3a3a;
    selection-background-color: #1e5a8e;
}

QTableWidget::item:selected {
    background-color: #1e5a8e;
}

QHeaderView::section {
    background-color: #3a3a3a;
    color: #ffffff;
    padding: 5px;
    border: 1px solid #2b2b2b;
}

QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: #3a3a3a;
    color: #ffffff;
    border: 1px solid #4a9eff;
    padding: 3px;
    border-radius: 2px;
}

QComboBox {
    background-color: #3a3a3a;
    color: #ffffff;
    border: 1px solid #4a9eff;
    padding: 3px;
}

QMenuBar {
    background-color: #2b2b2b;
    color: #ffffff;
}

QMenuBar::item:selected {
    background-color: #4a9eff;
}

QMenu {
    background-color: #3a3a3a;
    color: #ffffff;
    border: 1px solid #4a9eff;
}

QMenu::item:selected {
    background-color: #4a9eff;
}

QTabWidget::pane {
    border: 1px solid #4a9eff;
}

QTabBar::tab {
    background-color: #3a3a3a;
    color: #ffffff;
    padding: 8px 16px;
}

QTabBar::tab:selected {
    background-color: #4a9eff;
    color: #2b2b2b;
}

QScrollBar:vertical {
    background-color: #2b2b2b;
    width: 12px;
}

QScrollBar::handle:vertical {
    background-color: #4a9eff;
    border-radius: 6px;
}

QStatusBar {
    background-color: #3a3a3a;
    color: #ffffff;
}
"""

THEME_METADATA = {
    'name': 'Charcoal Theme',
    'description': 'Modern dark theme with blue accents',
    'author': 'PROGAIN Development Team',
    'version': '1.0',
    'type': 'dark'
}
