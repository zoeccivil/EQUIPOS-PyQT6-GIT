"""
Dim Theme for PROGAIN PyQt6 application.

General purpose dim theme
"""

THEME_STYLESHEET = """
QMainWindow {
    background-color: #1e1e1e;
    color: #d4d4d4;
}

QWidget {
    background-color: #1e1e1e;
    color: #d4d4d4;
}

QPushButton {
    background-color: #2d2d30;
    color: #d4d4d4;
    border: 1px solid #007acc;
    padding: 5px 15px;
    border-radius: 3px;
}

QPushButton:hover {
    background-color: #007acc;
    color: #1e1e1e;
}

QPushButton:pressed {
    background-color: #094771;
}

QTableWidget {
    background-color: #1e1e1e;
    alternate-background-color: #2d2d30;
    color: #d4d4d4;
    gridline-color: #2d2d30;
    selection-background-color: #094771;
}

QTableWidget::item:selected {
    background-color: #094771;
}

QHeaderView::section {
    background-color: #2d2d30;
    color: #d4d4d4;
    padding: 5px;
    border: 1px solid #1e1e1e;
}

QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: #2d2d30;
    color: #d4d4d4;
    border: 1px solid #007acc;
    padding: 3px;
    border-radius: 2px;
}

QComboBox {
    background-color: #2d2d30;
    color: #d4d4d4;
    border: 1px solid #007acc;
    padding: 3px;
}

QMenuBar {
    background-color: #1e1e1e;
    color: #d4d4d4;
}

QMenuBar::item:selected {
    background-color: #007acc;
}

QMenu {
    background-color: #2d2d30;
    color: #d4d4d4;
    border: 1px solid #007acc;
}

QMenu::item:selected {
    background-color: #007acc;
}

QTabWidget::pane {
    border: 1px solid #007acc;
}

QTabBar::tab {
    background-color: #2d2d30;
    color: #d4d4d4;
    padding: 8px 16px;
}

QTabBar::tab:selected {
    background-color: #007acc;
    color: #1e1e1e;
}

QScrollBar:vertical {
    background-color: #1e1e1e;
    width: 12px;
}

QScrollBar::handle:vertical {
    background-color: #007acc;
    border-radius: 6px;
}

QStatusBar {
    background-color: #2d2d30;
    color: #d4d4d4;
}
"""

THEME_METADATA = {
    'name': 'Dim Theme',
    'description': 'General purpose dim theme',
    'author': 'PROGAIN Development Team',
    'version': '1.0',
    'type': 'dark'
}
