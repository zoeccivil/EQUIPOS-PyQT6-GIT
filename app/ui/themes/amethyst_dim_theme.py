"""
Amethyst Dim Theme for PROGAIN PyQt6 application.

Purple/violet dim aesthetic
"""

THEME_STYLESHEET = """
QMainWindow {
    background-color: #2b2640;
    color: #e0d9f0;
}

QWidget {
    background-color: #2b2640;
    color: #e0d9f0;
}

QPushButton {
    background-color: #3b3650;
    color: #e0d9f0;
    border: 1px solid #9c27b0;
    padding: 5px 15px;
    border-radius: 3px;
}

QPushButton:hover {
    background-color: #9c27b0;
    color: #2b2640;
}

QPushButton:pressed {
    background-color: #6a1b9a;
}

QTableWidget {
    background-color: #2b2640;
    alternate-background-color: #3b3650;
    color: #e0d9f0;
    gridline-color: #3b3650;
    selection-background-color: #6a1b9a;
}

QTableWidget::item:selected {
    background-color: #6a1b9a;
}

QHeaderView::section {
    background-color: #3b3650;
    color: #e0d9f0;
    padding: 5px;
    border: 1px solid #2b2640;
}

QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: #3b3650;
    color: #e0d9f0;
    border: 1px solid #9c27b0;
    padding: 3px;
    border-radius: 2px;
}

QComboBox {
    background-color: #3b3650;
    color: #e0d9f0;
    border: 1px solid #9c27b0;
    padding: 3px;
}

QMenuBar {
    background-color: #2b2640;
    color: #e0d9f0;
}

QMenuBar::item:selected {
    background-color: #9c27b0;
}

QMenu {
    background-color: #3b3650;
    color: #e0d9f0;
    border: 1px solid #9c27b0;
}

QMenu::item:selected {
    background-color: #9c27b0;
}

QTabWidget::pane {
    border: 1px solid #9c27b0;
}

QTabBar::tab {
    background-color: #3b3650;
    color: #e0d9f0;
    padding: 8px 16px;
}

QTabBar::tab:selected {
    background-color: #9c27b0;
    color: #2b2640;
}

QScrollBar:vertical {
    background-color: #2b2640;
    width: 12px;
}

QScrollBar::handle:vertical {
    background-color: #9c27b0;
    border-radius: 6px;
}

QStatusBar {
    background-color: #3b3650;
    color: #e0d9f0;
}
"""

THEME_METADATA = {
    'name': 'Amethyst Dim Theme',
    'description': 'Purple/violet dim aesthetic',
    'author': 'PROGAIN Development Team',
    'version': '1.0',
    'type': 'dark'
}
