"""
Oceanic Dim Theme for PROGAIN PyQt6 application.

Ocean blue dim palette
"""

THEME_STYLESHEET = """
QMainWindow {
    background-color: #263a47;
    color: #cdd3de;
}

QWidget {
    background-color: #263a47;
    color: #cdd3de;
}

QPushButton {
    background-color: #364a57;
    color: #cdd3de;
    border: 1px solid #00bcd4;
    padding: 5px 15px;
    border-radius: 3px;
}

QPushButton:hover {
    background-color: #00bcd4;
    color: #263a47;
}

QPushButton:pressed {
    background-color: #0097a7;
}

QTableWidget {
    background-color: #263a47;
    alternate-background-color: #364a57;
    color: #cdd3de;
    gridline-color: #364a57;
    selection-background-color: #0097a7;
}

QTableWidget::item:selected {
    background-color: #0097a7;
}

QHeaderView::section {
    background-color: #364a57;
    color: #cdd3de;
    padding: 5px;
    border: 1px solid #263a47;
}

QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: #364a57;
    color: #cdd3de;
    border: 1px solid #00bcd4;
    padding: 3px;
    border-radius: 2px;
}

QComboBox {
    background-color: #364a57;
    color: #cdd3de;
    border: 1px solid #00bcd4;
    padding: 3px;
}

QMenuBar {
    background-color: #263a47;
    color: #cdd3de;
}

QMenuBar::item:selected {
    background-color: #00bcd4;
}

QMenu {
    background-color: #364a57;
    color: #cdd3de;
    border: 1px solid #00bcd4;
}

QMenu::item:selected {
    background-color: #00bcd4;
}

QTabWidget::pane {
    border: 1px solid #00bcd4;
}

QTabBar::tab {
    background-color: #364a57;
    color: #cdd3de;
    padding: 8px 16px;
}

QTabBar::tab:selected {
    background-color: #00bcd4;
    color: #263a47;
}

QScrollBar:vertical {
    background-color: #263a47;
    width: 12px;
}

QScrollBar::handle:vertical {
    background-color: #00bcd4;
    border-radius: 6px;
}

QStatusBar {
    background-color: #364a57;
    color: #cdd3de;
}
"""

THEME_METADATA = {
    'name': 'Oceanic Dim Theme',
    'description': 'Ocean blue dim palette',
    'author': 'PROGAIN Development Team',
    'version': '1.0',
    'type': 'dark'
}
