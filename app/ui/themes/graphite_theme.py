"""
Graphite Theme for PROGAIN PyQt6 application.

Sleek dark theme with green highlights
"""

THEME_STYLESHEET = """
QMainWindow {
    background-color: #2d2d2d;
    color: #e0e0e0;
}

QWidget {
    background-color: #2d2d2d;
    color: #e0e0e0;
}

QPushButton {
    background-color: #3d3d3d;
    color: #e0e0e0;
    border: 1px solid #4caf50;
    padding: 5px 15px;
    border-radius: 3px;
}

QPushButton:hover {
    background-color: #4caf50;
    color: #2d2d2d;
}

QPushButton:pressed {
    background-color: #2e7d32;
}

QTableWidget {
    background-color: #2d2d2d;
    alternate-background-color: #3d3d3d;
    color: #e0e0e0;
    gridline-color: #3d3d3d;
    selection-background-color: #2e7d32;
}

QTableWidget::item:selected {
    background-color: #2e7d32;
}

QHeaderView::section {
    background-color: #3d3d3d;
    color: #e0e0e0;
    padding: 5px;
    border: 1px solid #2d2d2d;
}

QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: #3d3d3d;
    color: #e0e0e0;
    border: 1px solid #4caf50;
    padding: 3px;
    border-radius: 2px;
}

QComboBox {
    background-color: #3d3d3d;
    color: #e0e0e0;
    border: 1px solid #4caf50;
    padding: 3px;
}

QMenuBar {
    background-color: #2d2d2d;
    color: #e0e0e0;
}

QMenuBar::item:selected {
    background-color: #4caf50;
}

QMenu {
    background-color: #3d3d3d;
    color: #e0e0e0;
    border: 1px solid #4caf50;
}

QMenu::item:selected {
    background-color: #4caf50;
}

QTabWidget::pane {
    border: 1px solid #4caf50;
}

QTabBar::tab {
    background-color: #3d3d3d;
    color: #e0e0e0;
    padding: 8px 16px;
}

QTabBar::tab:selected {
    background-color: #4caf50;
    color: #2d2d2d;
}

QScrollBar:vertical {
    background-color: #2d2d2d;
    width: 12px;
}

QScrollBar::handle:vertical {
    background-color: #4caf50;
    border-radius: 6px;
}

QStatusBar {
    background-color: #3d3d3d;
    color: #e0e0e0;
}
"""

THEME_METADATA = {
    'name': 'Graphite Theme',
    'description': 'Sleek dark theme with green highlights',
    'author': 'PROGAIN Development Team',
    'version': '1.0',
    'type': 'dark'
}
