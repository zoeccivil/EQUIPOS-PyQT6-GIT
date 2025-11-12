"""
Professional Light Theme for PROGAIN PyQt6 application.

Business-focused light theme
"""

THEME_STYLESHEET = """
QMainWindow {
    background-color: #f5f5f5;
    color: #333333;
}

QWidget {
    background-color: #f5f5f5;
    color: #333333;
}

QPushButton {
    background-color: #eeeeee;
    color: #333333;
    border: 1px solid #1976d2;
    padding: 5px 15px;
    border-radius: 3px;
}

QPushButton:hover {
    background-color: #1976d2;
    color: #f5f5f5;
}

QPushButton:pressed {
    background-color: #bbdefb;
}

QTableWidget {
    background-color: #f5f5f5;
    alternate-background-color: #eeeeee;
    color: #333333;
    gridline-color: #eeeeee;
    selection-background-color: #bbdefb;
}

QTableWidget::item:selected {
    background-color: #bbdefb;
}

QHeaderView::section {
    background-color: #eeeeee;
    color: #333333;
    padding: 5px;
    border: 1px solid #f5f5f5;
}

QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: #eeeeee;
    color: #333333;
    border: 1px solid #1976d2;
    padding: 3px;
    border-radius: 2px;
}

QComboBox {
    background-color: #eeeeee;
    color: #333333;
    border: 1px solid #1976d2;
    padding: 3px;
}

QMenuBar {
    background-color: #f5f5f5;
    color: #333333;
}

QMenuBar::item:selected {
    background-color: #1976d2;
}

QMenu {
    background-color: #eeeeee;
    color: #333333;
    border: 1px solid #1976d2;
}

QMenu::item:selected {
    background-color: #1976d2;
}

QTabWidget::pane {
    border: 1px solid #1976d2;
}

QTabBar::tab {
    background-color: #eeeeee;
    color: #333333;
    padding: 8px 16px;
}

QTabBar::tab:selected {
    background-color: #1976d2;
    color: #f5f5f5;
}

QScrollBar:vertical {
    background-color: #f5f5f5;
    width: 12px;
}

QScrollBar::handle:vertical {
    background-color: #1976d2;
    border-radius: 6px;
}

QStatusBar {
    background-color: #eeeeee;
    color: #333333;
}
"""

THEME_METADATA = {
    'name': 'Professional Light Theme',
    'description': 'Business-focused light theme',
    'author': 'PROGAIN Development Team',
    'version': '1.0',
    'type': 'light'
}
