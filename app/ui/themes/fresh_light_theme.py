"""
Fresh Light Theme for PROGAIN PyQt6 application.

Vibrant light theme with green accents
"""

THEME_STYLESHEET = """
QMainWindow {
    background-color: #fafafa;
    color: #212121;
}

QWidget {
    background-color: #fafafa;
    color: #212121;
}

QPushButton {
    background-color: #e8f5e9;
    color: #212121;
    border: 1px solid #4caf50;
    padding: 5px 15px;
    border-radius: 3px;
}

QPushButton:hover {
    background-color: #4caf50;
    color: #fafafa;
}

QPushButton:pressed {
    background-color: #c8e6c9;
}

QTableWidget {
    background-color: #fafafa;
    alternate-background-color: #e8f5e9;
    color: #212121;
    gridline-color: #e8f5e9;
    selection-background-color: #c8e6c9;
}

QTableWidget::item:selected {
    background-color: #c8e6c9;
}

QHeaderView::section {
    background-color: #e8f5e9;
    color: #212121;
    padding: 5px;
    border: 1px solid #fafafa;
}

QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: #e8f5e9;
    color: #212121;
    border: 1px solid #4caf50;
    padding: 3px;
    border-radius: 2px;
}

QComboBox {
    background-color: #e8f5e9;
    color: #212121;
    border: 1px solid #4caf50;
    padding: 3px;
}

QMenuBar {
    background-color: #fafafa;
    color: #212121;
}

QMenuBar::item:selected {
    background-color: #4caf50;
}

QMenu {
    background-color: #e8f5e9;
    color: #212121;
    border: 1px solid #4caf50;
}

QMenu::item:selected {
    background-color: #4caf50;
}

QTabWidget::pane {
    border: 1px solid #4caf50;
}

QTabBar::tab {
    background-color: #e8f5e9;
    color: #212121;
    padding: 8px 16px;
}

QTabBar::tab:selected {
    background-color: #4caf50;
    color: #fafafa;
}

QScrollBar:vertical {
    background-color: #fafafa;
    width: 12px;
}

QScrollBar::handle:vertical {
    background-color: #4caf50;
    border-radius: 6px;
}

QStatusBar {
    background-color: #e8f5e9;
    color: #212121;
}
"""

THEME_METADATA = {
    'name': 'Fresh Light Theme',
    'description': 'Vibrant light theme with green accents',
    'author': 'PROGAIN Development Team',
    'version': '1.0',
    'type': 'light'
}
