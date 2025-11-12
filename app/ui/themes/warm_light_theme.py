"""
Warm Light Theme for PROGAIN PyQt6 application.

Warm beige/cream tones
"""

THEME_STYLESHEET = """
QMainWindow {
    background-color: #faf8f3;
    color: #3e2723;
}

QWidget {
    background-color: #faf8f3;
    color: #3e2723;
}

QPushButton {
    background-color: #fff3e0;
    color: #3e2723;
    border: 1px solid #ff6f00;
    padding: 5px 15px;
    border-radius: 3px;
}

QPushButton:hover {
    background-color: #ff6f00;
    color: #faf8f3;
}

QPushButton:pressed {
    background-color: #ffe0b2;
}

QTableWidget {
    background-color: #faf8f3;
    alternate-background-color: #fff3e0;
    color: #3e2723;
    gridline-color: #fff3e0;
    selection-background-color: #ffe0b2;
}

QTableWidget::item:selected {
    background-color: #ffe0b2;
}

QHeaderView::section {
    background-color: #fff3e0;
    color: #3e2723;
    padding: 5px;
    border: 1px solid #faf8f3;
}

QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: #fff3e0;
    color: #3e2723;
    border: 1px solid #ff6f00;
    padding: 3px;
    border-radius: 2px;
}

QComboBox {
    background-color: #fff3e0;
    color: #3e2723;
    border: 1px solid #ff6f00;
    padding: 3px;
}

QMenuBar {
    background-color: #faf8f3;
    color: #3e2723;
}

QMenuBar::item:selected {
    background-color: #ff6f00;
}

QMenu {
    background-color: #fff3e0;
    color: #3e2723;
    border: 1px solid #ff6f00;
}

QMenu::item:selected {
    background-color: #ff6f00;
}

QTabWidget::pane {
    border: 1px solid #ff6f00;
}

QTabBar::tab {
    background-color: #fff3e0;
    color: #3e2723;
    padding: 8px 16px;
}

QTabBar::tab:selected {
    background-color: #ff6f00;
    color: #faf8f3;
}

QScrollBar:vertical {
    background-color: #faf8f3;
    width: 12px;
}

QScrollBar::handle:vertical {
    background-color: #ff6f00;
    border-radius: 6px;
}

QStatusBar {
    background-color: #fff3e0;
    color: #3e2723;
}
"""

THEME_METADATA = {
    'name': 'Warm Light Theme',
    'description': 'Warm beige/cream tones',
    'author': 'PROGAIN Development Team',
    'version': '1.0',
    'type': 'light'
}
