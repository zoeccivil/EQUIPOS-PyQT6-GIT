# EQUIPOS-PyQT6-GIT

Sistema de gestión de alquiler de equipos pesados con PyQt6 y Firestore.

## 🚀 Características

- **Gestión de alquileres** de equipos pesados
- **Dashboard** con estadísticas y gráficos
- **Control de pagos** a operadores
- **Gestión de gastos** por equipo
- **Reportes** en PDF y Excel
- **Estados de cuenta** detallados
- **Sincronización en tiempo real** con Firestore
- **Backups automáticos** a SQLite

## 📋 Requisitos

- Python 3.8 o superior
- PyQt6
- Conexión a internet (para Firestore)
- Cuenta de Firebase (gratis)

## 🔧 Instalación

1. **Clona el repositorio**
   ```bash
   git clone https://github.com/zoeccivil/EQUIPOS-PyQT6-GIT.git
   cd EQUIPOS-PyQT6-GIT
   ```

2. **Instala las dependencias**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configura Firestore** (primera vez)
   - Lee la guía completa en [FIRESTORE_SETUP.md](FIRESTORE_SETUP.md)
   - Crea un proyecto en [Firebase Console](https://console.firebase.google.com)
   - Habilita Firestore y Authentication
   - Ejecuta la aplicación y configura las credenciales

4. **Ejecuta la aplicación**
   ```bash
   python main_qt.py
   ```

## 📖 Documentación

### Arquitectura de Datos

Esta aplicación utiliza **Firestore como fuente de datos principal**:

- ✅ Todas las operaciones normales van a Firestore
- ✅ SQLite solo se usa para migraciones y backups
- ✅ Autenticación con email/password (no requiere JSON de service account)
- ✅ Sincronización en tiempo real entre dispositivos

### Configuración de Firestore

Consulta la guía detallada: [FIRESTORE_SETUP.md](FIRESTORE_SETUP.md)

Pasos rápidos:
1. Crear proyecto en Firebase
2. Habilitar Firestore Database
3. Habilitar Email/Password Authentication
4. Configurar credenciales en la app
5. (Opcional) Migrar datos existentes de SQLite

### Migración desde SQLite

Si tienes datos en SQLite:
1. Ve a **Herramientas > Migrar desde SQLite a Firestore...**
2. Selecciona tu archivo `.db`
3. Espera a que complete la migración
4. ¡Listo! Tus datos están en Firestore

### Backups

Crear backups locales desde Firestore:
1. Ve a **Herramientas > Crear Backup SQLite desde Firestore...**
2. Selecciona la carpeta de destino
3. Se creará un archivo `.db` con timestamp

## 🎯 Uso Principal

### Menús Principales

- **Archivo**: Backups, selección de BD, salir
- **Reportes**: Estados de cuenta, reportes de equipos y operadores
- **Gestión**: Clientes, operadores, equipos, mantenimientos, abonos
- **Herramientas**: Migración SQLite↔Firestore, backups, verificar conexión
- **Configuración**: Fuente de datos, carpeta de backups, carpeta de conduces

### Pestañas

1. **Registro de Alquileres**: Gestión principal de alquileres
2. **Gastos Equipos**: Control de gastos por equipo
3. **Pagos a Operadores**: Registro de pagos a operadores
4. **Dashboard**: Estadísticas y análisis visual

## 🔒 Seguridad

- **Credenciales**: Guardadas en `app_settings.json` (no se sube a Git)
- **Firestore**: Usa reglas de seguridad y autenticación
- **Backups**: Encriptados y en carpeta configurable
- **Logs**: Auditoría completa en `progain.log`

⚠️ **IMPORTANTE**: Nunca compartas tu `app_settings.json` ni subas credenciales a Git.

## 🛠️ Solución de Problemas

### No se puede conectar a Firestore
- Verifica tu conexión a internet
- Revisa las credenciales en **Configuración > Configurar Fuente de Datos**
- Consulta [FIRESTORE_SETUP.md](FIRESTORE_SETUP.md)

### Datos no aparecen
- Verifica que estés usando la fuente de datos correcta (Firestore/SQLite)
- Revisa en Firebase Console que los datos existen
- Ejecuta **Herramientas > Verificar Conexión Firestore**

### Error de migración
- La migración continúa aunque algunos registros fallen
- Revisa el log de la aplicación (`progain.log`)
- Puedes ejecutar la migración nuevamente (evita duplicados)

## 📄 Licencia

[Licencia del proyecto - agregar según corresponda]

## 👥 Contribuciones

Las contribuciones son bienvenidas. Por favor:
1. Haz fork del proyecto
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

## 📞 Soporte

Para soporte o consultas:
- Abre un issue en GitHub
- Revisa la documentación en [FIRESTORE_SETUP.md](FIRESTORE_SETUP.md)
- Contacta al administrador del sistema

---

Desarrollado con ❤️ para la gestión eficiente de equipos pesados
