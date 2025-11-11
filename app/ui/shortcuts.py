"""
Centralized keyboard shortcuts management for PROGAIN application.

Provides consistent keyboard shortcuts across all parts of the application:
- Global shortcuts (Ctrl+N, Ctrl+E, Del, etc.)
- Table-specific shortcuts (Enter, Ctrl+C, etc.)
- Automatic tooltip integration
- Context-aware actions
"""

from PyQt6.QtCore import Qt, QObject, pyqtSignal
from PyQt6.QtGui import QAction, QKeySequence
from PyQt6.QtWidgets import QWidget, QTableWidget, QTableView


class ShortcutsManager(QObject):
    """
    Manages keyboard shortcuts for the application.
    
    Usage:
        manager = ShortcutsManager(parent_widget)
        manager.setup_global_shortcuts(callback_dict)
        manager.setup_table_shortcuts(table_widget, callback_dict)
    """
    
    # Signals for shortcuts
    new_record = pyqtSignal()
    edit_record = pyqtSignal()
    delete_record = pyqtSignal()
    save_record = pyqtSignal()
    search = pyqtSignal()
    refresh = pyqtSignal()
    close_dialog = pyqtSignal()
    print_export = pyqtSignal()
    
    def __init__(self, parent: QWidget = None):
        super().__init__(parent)
        self.parent_widget = parent
        self.actions = {}
        
    def setup_global_shortcuts(self, callbacks: dict = None):
        """
        Setup global keyboard shortcuts.
        
        Args:
            callbacks: Dictionary mapping action names to callback functions
                      {'new': func, 'edit': func, 'delete': func, ...}
        """
        if callbacks is None:
            callbacks = {}
            
        shortcuts = [
            ('new', 'Ctrl+N', 'Nuevo', self.new_record, callbacks.get('new')),
            ('edit', 'Ctrl+E', 'Editar', self.edit_record, callbacks.get('edit')),
            ('delete', 'Del', 'Eliminar', self.delete_record, callbacks.get('delete')),
            ('save', 'Ctrl+S', 'Guardar', self.save_record, callbacks.get('save')),
            ('search', 'Ctrl+F', 'Buscar', self.search, callbacks.get('search')),
            ('refresh', 'F5', 'Refrescar', self.refresh, callbacks.get('refresh')),
            ('close', 'Esc', 'Cerrar/Cancelar', self.close_dialog, callbacks.get('close')),
            ('print', 'Ctrl+P', 'Imprimir/Exportar', self.print_export, callbacks.get('print')),
        ]
        
        for name, key, text, signal, callback in shortcuts:
            action = QAction(text, self.parent_widget)
            action.setShortcut(QKeySequence(key))
            
            # Set tooltip with shortcut hint
            action.setToolTip(f"{text} ({key})")
            
            # Connect signal
            if callback:
                action.triggered.connect(callback)
            else:
                action.triggered.connect(signal.emit)
            
            # Add to parent widget
            if self.parent_widget:
                self.parent_widget.addAction(action)
            
            self.actions[name] = action
            
    def setup_table_shortcuts(self, table, callbacks: dict = None):
        """
        Setup table-specific keyboard shortcuts.
        
        Args:
            table: QTableWidget or QTableView
            callbacks: Dictionary mapping action names to callback functions
        """
        if callbacks is None:
            callbacks = {}
            
        # Enter key to edit
        if callbacks.get('edit'):
            # Double-click to edit (already handled by table usually)
            if isinstance(table, (QTableWidget, QTableView)):
                table.doubleClicked.connect(lambda: callbacks['edit']())
                
        # Ctrl+C to copy
        copy_action = QAction("Copiar", table)
        copy_action.setShortcut(QKeySequence.StandardKey.Copy)
        copy_action.setToolTip("Copiar selección (Ctrl+C)")
        if callbacks.get('copy'):
            copy_action.triggered.connect(callbacks['copy'])
        table.addAction(copy_action)
        
        # Ctrl+A to select all
        select_all_action = QAction("Seleccionar todo", table)
        select_all_action.setShortcut(QKeySequence.StandardKey.SelectAll)
        select_all_action.setToolTip("Seleccionar todo (Ctrl+A)")
        if callbacks.get('select_all'):
            select_all_action.triggered.connect(callbacks['select_all'])
        else:
            select_all_action.triggered.connect(table.selectAll)
        table.addAction(select_all_action)
        
        # Ctrl+Backspace to clear filters
        clear_filter_action = QAction("Limpiar filtros", table)
        clear_filter_action.setShortcut(QKeySequence("Ctrl+Backspace"))
        clear_filter_action.setToolTip("Limpiar filtros (Ctrl+Backspace)")
        if callbacks.get('clear_filters'):
            clear_filter_action.triggered.connect(callbacks['clear_filters'])
        table.addAction(clear_filter_action)
        
    def get_action(self, name: str) -> QAction:
        """Get action by name."""
        return self.actions.get(name)
        
    def enable_action(self, name: str, enabled: bool = True):
        """Enable or disable an action."""
        if name in self.actions:
            self.actions[name].setEnabled(enabled)
            
    def set_action_text(self, name: str, text: str):
        """Update action text."""
        if name in self.actions:
            self.actions[name].setText(text)
            # Update tooltip to include shortcut
            shortcut = self.actions[name].shortcut().toString()
            self.actions[name].setToolTip(f"{text} ({shortcut})")


# Global shortcuts reference for documentation
GLOBAL_SHORTCUTS = {
    'Ctrl+N': 'Nuevo registro',
    'Ctrl+E': 'Editar seleccionado',
    'Del': 'Eliminar seleccionado',
    'Ctrl+S': 'Guardar',
    'Ctrl+F': 'Buscar/Filtrar',
    'F5': 'Refrescar',
    'Esc': 'Cerrar/Cancelar',
    'Ctrl+P': 'Imprimir/Exportar',
}

TABLE_SHORTCUTS = {
    'Enter': 'Editar fila seleccionada',
    'Double-click': 'Editar fila',
    'Ctrl+C': 'Copiar selección',
    'Ctrl+A': 'Seleccionar todo',
    'Ctrl+Backspace': 'Limpiar filtros',
    'Arrow Keys': 'Navegar',
    'Page Up/Down': 'Desplazamiento rápido',
    'Home/End': 'Primera/Última fila',
}


def get_shortcuts_help_text() -> str:
    """Get formatted help text for all shortcuts."""
    text = "=== Atajos de Teclado Globales ===\n\n"
    for key, desc in GLOBAL_SHORTCUTS.items():
        text += f"{key:20s} - {desc}\n"
    
    text += "\n=== Atajos en Tablas ===\n\n"
    for key, desc in TABLE_SHORTCUTS.items():
        text += f"{key:20s} - {desc}\n"
    
    return text


def copy_table_selection_as_csv(table) -> str:
    """
    Copy selected rows from table as CSV text.
    
    Args:
        table: QTableWidget or QTableView with selection
        
    Returns:
        CSV formatted string of selected data
    """
    if isinstance(table, QTableWidget):
        return _copy_qtablewidget_as_csv(table)
    elif isinstance(table, QTableView):
        return _copy_qtableview_as_csv(table)
    return ""


def _copy_qtablewidget_as_csv(table: QTableWidget) -> str:
    """Copy QTableWidget selection as CSV."""
    selected_ranges = table.selectedRanges()
    if not selected_ranges:
        return ""
    
    lines = []
    for range in selected_ranges:
        for row in range(range.topRow(), range.bottomRow() + 1):
            row_data = []
            for col in range(range.leftColumn(), range.rightColumn() + 1):
                item = table.item(row, col)
                row_data.append(item.text() if item else "")
            lines.append("\t".join(row_data))
    
    return "\n".join(lines)


def _copy_qtableview_as_csv(table: QTableView) -> str:
    """Copy QTableView selection as CSV."""
    selection = table.selectionModel()
    if not selection.hasSelection():
        return ""
    
    indexes = selection.selectedIndexes()
    if not indexes:
        return ""
    
    # Group by row
    rows = {}
    for index in indexes:
        row = index.row()
        if row not in rows:
            rows[row] = {}
        rows[row][index.column()] = index.data()
    
    # Build CSV
    lines = []
    for row in sorted(rows.keys()):
        row_data = []
        for col in sorted(rows[row].keys()):
            data = rows[row][col]
            row_data.append(str(data) if data is not None else "")
        lines.append("\t".join(row_data))
    
    return "\n".join(lines)
