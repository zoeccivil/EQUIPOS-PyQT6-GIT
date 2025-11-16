import sys
import os
import shutil
import logging
from datetime import datetime, date
from PIL import Image

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, QComboBox, QDateEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QHeaderView, QFileDialog,
    QApplication  # <-- 1. IMPORT AÑADIDO
)
from PyQt6.QtCore import QDate, Qt

from dialogo_alquiler import DialogoAlquiler
from ventana_gestion_abonos import DialogoRegistroAbono
from mini_editor_imagen import MiniEditorImagen 
from DialogoPagoOperador import DialogoPagoOperador

logging.basicConfig(
    filename='progain.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s %(message)s'
)

logger = logging.getLogger(__name__)  # <--- ¡AÑADE ESTA LÍNEA AQUÍ!

class RegistroAlquileresTab(QWidget):
    # --- 2. __INIT__ MODIFICADO ---
    def __init__(self, db_manager, proyecto_actual, config):
            super().__init__()
            self.db = db_manager
            self.proyecto_actual = proyecto_actual
            self.config = config

            self.cliente_filtro = "Todos"
            self.equipo_filtro = "Todos"
            self.operador_filtro = "Todos"
            self.clientes_mapa = {}
            self.equipos_mapa = {}
            self.operadores_mapa = {}

            # self.ha_sincronizado_transacciones = False <-- BORRA ESTA LÍNEA

            self._setup_ui()
            self.poblar_filtros()   # <-- ESTA LÍNEA DEBE ESTAR AQUÍ
            self.refrescar_tabla()  # <-- ESTA LÍNEA DEBE ESTAR AQUÍ

    def _setup_ui(self):
        main_layout = QVBoxLayout(self)

        # === Filtros ===
        filtros_group = QGroupBox("Filtros")
        filtros_layout = QHBoxLayout()
        filtros_group.setLayout(filtros_layout)

        self.combo_operador = QComboBox()
        self.combo_operador.addItem("Todos")
        filtros_layout.addWidget(QLabel("Operador:"))
        filtros_layout.addWidget(self.combo_operador)

        self.fecha_inicio = QDateEdit()
        self.fecha_inicio.setCalendarPopup(True)
        self.fecha_inicio.setDate(QDate.currentDate())
        filtros_layout.addWidget(QLabel("Desde:"))
        filtros_layout.addWidget(self.fecha_inicio)

        self.fecha_fin = QDateEdit()
        self.fecha_fin.setCalendarPopup(True)
        self.fecha_fin.setDate(QDate.currentDate())
        filtros_layout.addWidget(QLabel("Hasta:"))
        filtros_layout.addWidget(self.fecha_fin)

        self.combo_cliente = QComboBox()
        self.combo_cliente.addItem("Todos")
        filtros_layout.addWidget(QLabel("Cliente:"))
        filtros_layout.addWidget(self.combo_cliente)

        self.combo_equipo = QComboBox()
        self.combo_equipo.addItem("Todos")
        filtros_layout.addWidget(QLabel("Equipo:"))
        filtros_layout.addWidget(self.combo_equipo)

        main_layout.addWidget(filtros_group)

        # === Botones de acción ===
        btn_layout = QHBoxLayout()
        self.btn_registrar = QPushButton("Registrar Alquiler")
        self.btn_editar = QPushButton("Editar Alquiler")
        self.btn_eliminar = QPushButton("Eliminar Alquiler")
        self.btn_registrar_abono = QPushButton("Registrar Abono")
        self.btn_adjuntar_conduce = QPushButton("Adjuntar Conduce")
        btn_layout.addWidget(self.btn_registrar)
        btn_layout.addWidget(self.btn_editar)
        btn_layout.addWidget(self.btn_eliminar)
        btn_layout.addWidget(self.btn_registrar_abono)
        btn_layout.addWidget(self.btn_adjuntar_conduce)
        btn_layout.addStretch(1)
        main_layout.addLayout(btn_layout)

        # Conexiones de botones
        self.btn_registrar.clicked.connect(self.registrar_alquiler)
        self.btn_editar.clicked.connect(self.on_editar_alquiler_boton)
        self.btn_eliminar.clicked.connect(self.on_eliminar_alquiler_boton)
        self.btn_registrar_abono.clicked.connect(self.funcion_registrar_abono)
        self.btn_adjuntar_conduce.clicked.connect(self.on_adjuntar_conduce)

        # === Tabla principal ===
        self.table = QTableWidget(0, 10)
        self.table.setHorizontalHeaderLabels([
            'Fecha', 'Conduce', 'Cliente', 'Operador', 'Equipo', 'Ubicación',
            'Horas', 'Precio/hora', 'Monto', 'Pagado'
        ])

        self.btn_ver_conduce = QPushButton("Ver Conduce")
        btn_layout.addWidget(self.btn_ver_conduce)
        self.btn_ver_conduce.clicked.connect(self.on_ver_conduce)
        main_layout.addWidget(self.table)
        self.table.cellDoubleClicked.connect(self.on_tabla_doble_clic)

        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        # === Indicadores inferiores ===
        indicadores_layout = QHBoxLayout()
        self.lbl_total_facturado = QLabel("Facturado: RD$ 0.00")
        self.lbl_total_abonado = QLabel("Pagado: RD$ 0.00")
        self.lbl_total_pendiente = QLabel("Pendiente: RD$ 0.00")
        self.lbl_total_horas = QLabel("Horas Totales: 0.00")
        indicadores_layout.addWidget(self.lbl_total_facturado)
        indicadores_layout.addWidget(self.lbl_total_abonado)
        indicadores_layout.addWidget(self.lbl_total_pendiente)
        indicadores_layout.addWidget(self.lbl_total_horas)
        main_layout.addLayout(indicadores_layout)

        # === Señales para refrescar los datos al cambiar filtros ===
        self.combo_cliente.currentIndexChanged.connect(self.refrescar_tabla)
        self.combo_operador.currentIndexChanged.connect(self.refrescar_tabla)
        self.combo_equipo.currentIndexChanged.connect(self.refrescar_tabla)
        self.fecha_inicio.dateChanged.connect(self.refrescar_tabla)
        self.fecha_fin.dateChanged.connect(self.refrescar_tabla)

    def on_ver_conduce(self):
        selected = self.table.currentRow()
        if selected == -1:
            QMessageBox.warning(self, "Advertencia", "Selecciona una fila.")
            return
        # Usar columna 10: conduce_adjunto_path (ruta relativa)
        conduce_path = self.table.item(selected, 10).text()
        self.abrir_conduce_adjunto(conduce_path)

    def on_tabla_doble_clic(self, row, column):
        conduce_path = self.table.item(row, 10).text()
        self.abrir_conduce_adjunto(conduce_path)

    # --- 3. NUEVA FUNCIÓN AÑADIDA ---
    def sincronizar_datos_bajo_demanda(self):
        """
        Verifica si las tablas de historial de esta pestaña ya se sincronizaron.
        Si no, las descarga de Firestore y las inserta en la BD local.
        """
        # 1. Si no hay repositorio (modo SQLite legacy) o ya sincronizamos, no hacer nada.
        if not self.repo or self.ha_sincronizado_transacciones:
            return

        # 2. Tablas que esta pestaña necesita (las que omitimos en main_qt.py)
        tablas_a_sincronizar = [
            "transacciones",
            "equipos_alquiler_meta",
            "pagos"
        ]

        # 3. Mostrar un mensaje al usuario
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle("Sincronizando Historial")
        msg_box.setText("Cargando historial de alquileres y pagos desde la nube... Por favor, espere.")
        msg_box.setStandardButtons(QMessageBox.StandardButton.NoButton) # Sin botones
        msg_box.show()
        QApplication.processEvents() # Forzar que la GUI se actualice

        logger.info(f"Carga Bajo Demanda: Sincronizando {tablas_a_sincronizar}...")

        try:
            for tabla in tablas_a_sincronizar:
                logger.info(f"Sincronizando tabla: {tabla}...")
                
                # --- Esta lógica es la misma que usamos en main_qt.py ---
                
                # A. Obtener columnas de la BD local
                columnas_sqlite = self.db.obtener_columnas_de_tabla(tabla)
                if not columnas_sqlite:
                    logger.warning(f"No se pudieron obtener columnas para la tabla SQLite '{tabla}'. Omitiendo.")
                    continue

                # B. Crear mapa de mapeo (snake_case -> camelCase)
                mapa_columnas = {}
                for col_sqlite in columnas_sqlite:
                    partes = col_sqlite.split('_')
                    col_camel = partes[0] + ''.join(p.capitalize() for p in partes[1:])
                    mapa_columnas[col_sqlite] = [col_sqlite, col_camel]
                
                # C. Obtener datos de Firestore (¡con reintentos!)
                registros_fs = self.repo.obtener_tabla_completa(tabla)
                
                if not registros_fs:
                    logger.info(f"Tabla {tabla} está vacía en Firestore. Omitiendo.")
                    continue
                
                # D. Insertar datos en la BD local (self.db)
                registros_insertados_count = 0
                for registro_fs_raw in registros_fs:
                    try:
                        registro_fs_limpio = {k: v for k, v in registro_fs_raw.items() if not k.startswith('_firestore')}
                        datos_a_insertar = {}
                        
                        for col_sqlite, posibles_nombres_fs in mapa_columnas.items():
                            if posibles_nombres_fs[0] in registro_fs_limpio:
                                datos_a_insertar[col_sqlite] = registro_fs_limpio[posibles_nombres_fs[0]]
                            elif posibles_nombres_fs[1] in registro_fs_limpio:
                                datos_a_insertar[col_sqlite] = registro_fs_limpio[posibles_nombres_fs[1]]
                        
                        if not datos_a_insertar:
                            continue

                        columns = list(datos_a_insertar.keys())
                        placeholders = ', '.join(['?' for _ in columns])
                        column_names = ', '.join(columns)
                        query = f"INSERT OR REPLACE INTO {tabla} ({column_names}) VALUES ({placeholders})"
                        
                        values = []
                        for col in columns:
                            val = datos_a_insertar[col]
                            if isinstance(val, str) and (col.endswith('_id') or col == 'id'):
                                try: values.append(int(val))
                                except (ValueError, TypeError): values.append(val)
                            else:
                                values.append(val)
                        
                        self.db.execute(query, values)
                        registros_insertados_count += 1

                    except Exception as e:
                        logger.warning(f"Error insertando registro individual en {tabla} (ID: {registro_fs_raw.get('id', 'N/A')}): {e}")
                        continue
                
                logger.info(f"✓ Carga Bajo Demanda: {registros_insertados_count} / {len(registros_fs)} registros de {tabla} insertados.")
                
                # --- FIN de la lógica copiada ---

            # 4. Marcar la bandera como completada
            self.ha_sincronizado_transacciones = True
            logger.info("Carga Bajo Demanda completada.")

        except Exception as e:
            logger.error(f"Error fatal durante Carga Bajo Demanda: {e}", exc_info=True)
            QMessageBox.critical(self, "Error de Sincronización", f"No se pudo cargar el historial: {e}")
        
        finally:
            # 5. Cerrar el mensaje de "cargando"
            msg_box.accept()

        # --- AÑADE ESTE BLOQUE ---
        # Si acabamos de sincronizar por primera vez,
        # repoblamos los filtros. Esto actualizará las
        # fechas de inicio/fin al rango correcto.
        if self.ha_sincronizado_transacciones:
            logger.info("Carga Bajo Demanda completada. Repoblando filtros...")
            self.poblar_filtros()
            logger.info("Filtros repoblados con las fechas correctas.")
        # --- FIN DEL BLOQUE AÑADIDO ---
    # --- 4. refrescar_tabla MODIFICADO ---
    def refrescar_tabla(self):
        # Primero, asegurar que los datos estén sincronizados
        #self.sincronizar_datos_bajo_demanda()

        self.table.setRowCount(0)
        if not self.proyecto_actual:
            return
        filtros = self.get_current_filters()
        
        # Guardamos los resultados en una variable de la clase
        self.transacciones_actuales = self.db.obtener_transacciones_por_proyecto(self.proyecto_actual['id'], filtros)
        
        # El resto de la función usa esta nueva variable en lugar de llamar a la DB de nuevo
        transacciones = self.transacciones_actuales 
        
        total_facturado = 0
        # ... el resto de la función sigue exactamente igual ...
        total_abonado = 0
        total_horas = 0.0
        self.table.setColumnCount(11)
        self.table.setHorizontalHeaderLabels([
            'Fecha', 'Conduce', 'Cliente', 'Operador', 'Equipo', 'Ubicación',
            'Horas', 'Precio/hora', 'Monto', 'Pagado', 'ConduceAdjunto'
        ])
        for row, trans in enumerate(transacciones):
            self.table.insertRow(row)
            item_fecha = QTableWidgetItem(str(trans['fecha']))
            item_fecha.setData(Qt.ItemDataRole.UserRole, str(trans['id']))  # Guardar el id real aquí
            self.table.setItem(row, 0, item_fecha)
            self.table.setItem(row, 1, QTableWidgetItem(str(trans['conduce']) if 'conduce' in trans.keys() else ''))
            self.table.setItem(row, 2, QTableWidgetItem(str(trans['cliente_nombre']) if 'cliente_nombre' in trans.keys() else ''))
            self.table.setItem(row, 3, QTableWidgetItem(str(trans['operador_nombre']) if 'operador_nombre' in trans.keys() else ''))
            self.table.setItem(row, 4, QTableWidgetItem(str(trans['equipo_nombre']) if 'equipo_nombre' in trans.keys() else ''))
            self.table.setItem(row, 5, QTableWidgetItem(str(trans['ubicacion']) if 'ubicacion' in trans.keys() else ''))
            self.table.setItem(row, 6, QTableWidgetItem(str(trans['horas']) if 'horas' in trans.keys() else ''))
            self.table.setItem(row, 7, QTableWidgetItem(str(trans['precio_por_hora']) if 'precio_por_hora' in trans.keys() else ''))
            self.table.setItem(row, 8, QTableWidgetItem(str(trans['monto']) if 'monto' in trans.keys() else ''))
            pagado = trans['pagado'] if 'pagado' in trans.keys() else False
            self.table.setItem(row, 9, QTableWidgetItem("Pagado" if pagado else "Pendiente"))
            # Nueva columna oculta: conduce_adjunto_path (ruta relativa)
            self.table.setItem(row, 10, QTableWidgetItem(str(trans['conduce_adjunto_path']) if 'conduce_adjunto_path' in trans.keys() else ''))
            total_facturado += trans['monto'] if 'monto' in trans.keys() and trans['monto'] else 0
            total_horas += trans['horas'] if 'horas' in trans.keys() and trans['horas'] else 0
            if pagado:
                total_abonado += trans['monto'] if 'monto' in trans.keys() and trans['monto'] else 0
        self.lbl_total_facturado.setText(f"Facturado: RD$ {total_facturado:,.2f}")
        self.lbl_total_abonado.setText(f"Pagado: RD$ {total_abonado:,.2f}")
        self.lbl_total_pendiente.setText(f"Pendiente: RD$ {total_facturado-total_abonado:,.2f}")
        self.lbl_total_horas.setText(f"Horas Totales: {total_horas:.2f}")
        # Oculta la columna de la ruta
        self.table.setColumnHidden(10, True)

    def get_current_filters(self):
        filtros = {}
        filtros['fecha_inicio'] = self.fecha_inicio.date().toString("yyyy-MM-dd")
        filtros['fecha_fin'] = self.fecha_fin.date().toString("yyyy-MM-dd")
        cliente = self.combo_cliente.currentText()
        operador = self.combo_operador.currentText()
        equipo = self.combo_equipo.currentText()
        if cliente != "Todos":
            filtros['cliente_id'] = self.clientes_mapa.get(cliente)
        if operador != "Todos":
            filtros['operador_id'] = self.operadores_mapa.get(operador)
        if equipo != "Todos":
            filtros['equipo_id'] = self.equipos_mapa.get(equipo)
        return filtros

# En la clase RegistroAlquileresTab

    def registrar_alquiler(self):
        dlg = DialogoAlquiler(
            self.db, self.proyecto_actual,
            self.clientes_mapa, self.operadores_mapa, self.equipos_mapa,
            alquiler=None,
            config=self.config, # <-- AÑADIR ESTA LÍNEA
            parent=self
        )
        if dlg.exec():
            self.refrescar_tabla()

    def on_editar_alquiler_boton(self):
        selected = self.table.currentRow()
        if selected == -1:
            QMessageBox.warning(self, "Advertencia", "Selecciona una fila para editar.")
            return
        item = self.table.item(selected, 0)
        alquiler_id = item.data(Qt.ItemDataRole.UserRole)
        if not alquiler_id:
            QMessageBox.warning(self, "Error", "No se pudo encontrar el ID del alquiler.")
            return
        self.editar_alquiler(alquiler_id)

    def editar_alquiler(self, transaccion_id):
        datos = self.db.obtener_detalles_alquiler(transaccion_id)
        if not datos:
            QMessageBox.warning(self, "Error", "No se pudieron cargar los datos del alquiler.")
            return

        print(f"[DEBUG] Llamando DialogoAlquiler (edición) con config: {self.config}")
        dialog = DialogoAlquiler(
            self.db, self.proyecto_actual,
            self.clientes_mapa, self.operadores_mapa, self.equipos_mapa,
            alquiler=dict(datos), config=self.config, parent=self
        )
        if dialog.exec():
            nuevos_datos = dialog.get_datos()
            self.db.actualizar_alquiler(transaccion_id, nuevos_datos)
            QMessageBox.information(self, "Éxito", "Alquiler actualizado correctamente.")
            self.refrescar_tabla()


    def on_eliminar_alquiler_boton(self):
        selected = self.table.currentRow()
        if selected == -1:
            QMessageBox.warning(self, "Advertencia", "Selecciona una fila para eliminar.")
            return
        item = self.table.item(selected, 0)
        alquiler_id = item.data(Qt.ItemDataRole.UserRole)
        if not alquiler_id:
            QMessageBox.warning(self, "Error", "No se pudo encontrar el ID del alquiler.")
            return
        confirm = QMessageBox.question(
            self, "Confirmar", "¿Eliminar el alquiler seleccionado?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        if confirm == QMessageBox.StandardButton.Yes:
            exito = self.db.eliminar_alquiler(alquiler_id)
            if exito:
                QMessageBox.information(self, "Éxito", "Alquiler eliminado.")
                self.refrescar_tabla()
            else:
                QMessageBox.warning(self, "Error", "No se pudo eliminar el alquiler.")

    def poblar_filtros(self):
            if not self.proyecto_actual:
                return
                
            # --- ¡ASEGÚRATE DE TENER ESTA CORRECCIÓN! ---
            self.fecha_inicio.blockSignals(True)
            self.fecha_fin.blockSignals(True)
            # ---------------------------------------------
                
            # (El resto de la función sigue igual...)
            clientes = self.db.obtener_entidades_equipo_por_tipo(self.proyecto_actual['id'], "Cliente")
            self.clientes_mapa = {c['nombre']: c['id'] for c in clientes}
            self.combo_cliente.blockSignals(True)
            # ... (más código) ...
            self.combo_equipo.blockSignals(False)
            
            primera_fecha_str = self.db.obtener_fecha_primera_transaccion(self.proyecto_actual['id'])
            if primera_fecha_str:
                try:
                    primera_fecha = datetime.strptime(primera_fecha_str, "%Y-%m-%d").date()
                except Exception:
                    primera_fecha = date.today().replace(day=1)
            else:
                primera_fecha = date.today().replace(day=1)
                
            self.fecha_inicio.setDate(QDate(primera_fecha.year, primera_fecha.month, primera_fecha.day))
            self.fecha_fin.setDate(QDate.currentDate())

            # --- ¡Y ESTA PARTE! ---
            self.fecha_inicio.blockSignals(False)
            self.fecha_fin.blockSignals(False)
            # ---------------------
        #         
    def obtener_alquiler_seleccionado(self):
        fila_actual = self.table.currentRow()
        if fila_actual < 0:
            return None
            
        item = self.table.item(fila_actual, 0)
        alquiler_id = item.data(Qt.ItemDataRole.UserRole)
        if not alquiler_id:
            return None
            
        # Busca en la lista guardada en memoria, no en la base de datos
        for trans in self.transacciones_actuales:
            if str(trans['id']) == str(alquiler_id):
                return trans
                
        return None

    def funcion_registrar_pago_operador(self):
        QMessageBox.information(self, "Info", "Registrar pago a operador no implementado todavía.")

    def funcion_registrar_abono(self):
        dlg = DialogoRegistroAbono(self.db, self.proyecto_actual, parent=self)
        dlg.abono_registrado.connect(self.refrescar_tabla)
        dlg.exec()

    def procesar_y_guardar_imagen(origen, destino, width=1200, height=800):
        with Image.open(origen) as img:
            img = img.convert("RGB")
            img = img.resize((width, height), Image.LANCZOS)
            img.save(destino, format="JPEG", quality=90)

# Reemplaza las funciones on_adjuntar_conduce y abrir_conduce_adjunto por estas.
# Asegúrate de tener importados estos nombres al inicio del archivo:
# import os, shutil, tempfile, logging, re, sys
# from PyQt6.QtWidgets import QMessageBox, QFileDialog
# from mini_editor_imagen import MiniEditorImagen

    def on_adjuntar_conduce(self):
        selected_row = self.obtener_alquiler_seleccionado()
        if not selected_row:
            QMessageBox.warning(self, "Sin selección", "Debe seleccionar un alquiler para adjuntar el conduce.")
            return

        transaccion_id = selected_row.get('id')
        fecha_str = selected_row.get('fecha', '')
        conduce_num = selected_row.get('conduce') or str(transaccion_id)

        try:
            from datetime import datetime
            fecha_dt = datetime.strptime(fecha_str, "%Y-%m-%d")
            anio = str(fecha_dt.year)
            mes = f"{fecha_dt.month:02d}"
        except Exception:
            anio = "desconocido"
            mes = "00"

        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar archivo de Conduce",
            "",
            "Imágenes o PDFs (*.png *.jpg *.jpeg *.pdf);;Todos los archivos (*)"
        )
        if not file_path:
            return

        file_path = os.path.abspath(file_path)
        ext = os.path.splitext(file_path)[1].lower()

        # Preguntar al usuario si desea copiar el archivo al almacenamiento del proyecto
        resp = QMessageBox.question(
            self,
            "¿Copiar archivo?",
            ("¿Deseas copiar el archivo seleccionado al almacenamiento del proyecto?\n\n"
            "Sí = copiar el archivo dentro de la carpeta configurada (recomendado).\n"
            "No = mantener la ruta original (se guardará la ruta absoluta y no se copiará)."),
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        copiar_al_proyecto = (resp == QMessageBox.StandardButton.Yes)

        base_dir = getattr(self, 'config', {}).get('carpeta_conduces', './adjuntos')
        base_dir = os.path.expanduser(base_dir)
        if not os.path.isabs(base_dir):
            base_dir = os.path.abspath(base_dir)

        # Si el usuario eligió no copiar, almacenamos la ruta absoluta y no hacemos edición local.
        if not copiar_al_proyecto:
            # Si es imagen y quieres editar en el futuro, advierte que la edición no se hará.
            if ext in (".jpg", ".jpeg", ".png"):
                info = QMessageBox.question(
                    self,
                    "Editar imagen",
                    ("Has elegido no copiar el archivo al proyecto. Si deseas editar la imagen antes de guardar, "
                    "debes copiarla al proyecto. ¿Deseas copiar y editar ahora?"),
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if info == QMessageBox.StandardButton.Yes:
                    copiar_al_proyecto = True  # forzamos copia para permitir edición

        path_to_store = None
        temp_to_remove = None

        if copiar_al_proyecto:
            # Validar que la unidad exista (especialmente en Windows)
            drive, _ = os.path.splitdrive(base_dir)
            if drive and not os.path.exists(drive + os.sep):
                QMessageBox.warning(
                    self,
                    "Unidad no disponible",
                    (f"La unidad configurada para almacenar conduces ({drive}) no está disponible.\n"
                    "Se usará la carpeta local './adjuntos' como fallback.")
                )
                base_dir = os.path.abspath('./adjuntos')

            # Intentar crear base y subcarpeta año/mes
            try:
                destino_dir = os.path.join(base_dir, anio, mes)
                os.makedirs(destino_dir, exist_ok=True)
            except Exception as e:
                logging.exception("No se pudo crear destino_dir %s: %s", destino_dir, e)
                # Intentar fallback a ./adjuntos
                try:
                    base_dir = os.path.abspath('./adjuntos')
                    destino_dir = os.path.join(base_dir, anio, mes)
                    os.makedirs(destino_dir, exist_ok=True)
                except Exception as e2:
                    logging.exception("Fallback también falló: %s", e2)
                    QMessageBox.critical(self, "Error", f"No se pudo crear la carpeta destino para guardar el conduce:\n{e2}")
                    return

            nombre_archivo = f"{conduce_num}.jpeg" if ext in (".jpg", ".jpeg", ".png") else f"{conduce_num}{ext}"
            destino = os.path.join(destino_dir, nombre_archivo)

            # Si es imagen, abrir editor; si usuario cancela, abortar
            if ext in (".jpg", ".jpeg", ".png"):
                editor = MiniEditorImagen(file_path, width=1200, height=800, parent=self)
                if editor.exec():
                    final_img = editor.get_final_image()
                    try:
                        final_img.save(destino, format="JPEG", quality=90)
                        logging.info("Imagen editada y guardada en: %s", destino)
                    except Exception as e:
                        logging.exception("Error guardando imagen editada: %s", e)
                        QMessageBox.critical(self, "Error", f"No se pudo guardar la imagen editada:\n{e}")
                        return
                else:
                    # Usuario canceló editor; no continuar con copia
                    return
            else:
                # No es imagen: copiar archivo
                try:
                    shutil.copyfile(file_path, destino)
                    logging.info("Archivo copiado (no imagen): %s", destino)
                except Exception as e:
                    logging.exception("Error copiando archivo: %s", e)
                    QMessageBox.critical(self, "Error", f"No se pudo copiar el archivo:\n{e}")
                    return

            # Guardar ruta relativa respecto a base_dir
            path_to_store = os.path.relpath(destino, base_dir).replace("\\", "/")
            # Si por alguna razón se resolviera mejor guardar absoluta, podrías guardarla aquí.
        else:
            # No copiamos: guardamos la ruta absoluta del archivo seleccionado
            path_to_store = file_path

        # Actualizar DB
        try:
            self.db.actualizar_conduce_adjunto(transaccion_id, path_to_store)
        except Exception as e:
            logging.exception("No se pudo actualizar la DB con la ruta del conduce: %s", e)
            QMessageBox.warning(self, "Error DB", f"No se pudo guardar la ruta en la base de datos:\n{e}")
            # Si habíamos creado un archivo temporal o copiado algo, podríamos limpiar, pero aquí no hacemos limpieza automática.
            return
        finally:
            # Eliminar temporales si los hubiéramos creado (no usados en esta versión, pero por si se extiende)
            if temp_to_remove:
                try:
                    os.remove(temp_to_remove)
                except Exception:
                    pass

        QMessageBox.information(self, "Éxito", "Conduce adjuntado correctamente.")
        self.refrescar_tabla()


    def abrir_conduce_adjunto(self, conduce_rel_path):
        if not conduce_rel_path or str(conduce_rel_path).strip() == "":
            QMessageBox.warning(self, "Sin archivo", "No hay archivo de conduce adjunto para esta fila.")
            return

        # Si la ruta almacenada es absoluta (incluye UNC y letras de unidad), usarla tal cual.
        conduce_path_str = str(conduce_rel_path)
        conduce_abspath = None

        # Considerar rutas estilo 'E:/...' o '\\server\share...' o rutas absolutas POSIX
        if os.path.isabs(conduce_path_str) or conduce_path_str.startswith('\\\\'):
            conduce_abspath = os.path.abspath(conduce_path_str)
        else:
            # ruta relativa: resolver respecto a carpeta configurada
            base_dir = getattr(self, 'config', {}).get('carpeta_conduces', './adjuntos')
            base_dir = os.path.expanduser(base_dir)
            if not os.path.isabs(base_dir):
                base_dir = os.path.abspath(base_dir)
            conduce_abspath = os.path.abspath(os.path.join(base_dir, conduce_path_str.replace('/', os.sep)))

        logging.debug("Intentando abrir conduce: %s (entrada: %s)", conduce_abspath, conduce_rel_path)

        if not os.path.isfile(conduce_abspath):
            QMessageBox.warning(self, "Archivo no encontrado", f"No se encontró el archivo:\n{conduce_abspath}")
            return

        try:
            if sys.platform.startswith('darwin'):  # macOS
                os.system(f'open "{conduce_abspath}"')
            elif os.name == 'nt':  # Windows
                os.startfile(conduce_abspath)
            elif os.name == 'posix':  # Linux
                os.system(f'xdg-open "{conduce_abspath}"')
            else:
                QMessageBox.information(self, "Plataforma no soportada", f"Archivo: {conduce_abspath}")
        except Exception as e:
            logging.exception("No se pudo abrir el archivo: %s", e)
            QMessageBox.critical(self, "Error", f"No se pudo abrir el archivo:\n{e}")

    def _abrir_dialogo_pago_operador(self):
        dialogo = DialogoPagoOperador(self.db, self.proyecto_id, self)
        if dialogo.exec():
            # Aquí puedes recargar tablas relacionadas si lo deseas
            if hasattr(self, "tab_pagos_operadores"):
                self.tab_pagos_operadores._cargar_filtros()
                self.tab_pagos_operadores._cargar_pagos()