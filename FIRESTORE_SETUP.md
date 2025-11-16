# Configuración de Firestore para EQUIPOS-PyQT6-GIT

## Arquitectura de Datos

Esta aplicación ahora utiliza **Firestore como fuente de datos principal**, con SQLite solo para migraciones y backups.

### Flujo de Datos

```
┌─────────────────────────────────────────────────────┐
│                  FIRESTORE                          │
│         (Fuente de Datos Principal)                 │
│                                                     │
│  - Proyectos, Equipos, Clientes                    │
│  - Alquileres, Transacciones                       │
│  - Pagos, Mantenimientos                           │
└─────────────────────────────────────────────────────┘
           ▲                          │
           │                          │
      (Lectura/                   (Backup)
      Escritura)                      │
           │                          ▼
┌──────────────────────┐    ┌──────────────────┐
│   Aplicación PyQt6   │    │  SQLite Backups  │
│                      │    │  (./backups/)    │
└──────────────────────┘    └──────────────────┘
           │
           │ (Migración inicial)
           ▼
┌──────────────────────┐
│  SQLite Legacy DB    │
│  (Solo lectura)      │
└──────────────────────┘
```

## Configuración Inicial de Firestore

### 1. Crear Proyecto en Firebase

1. Ve a [Firebase Console](https://console.firebase.google.com)
2. Haz clic en "Agregar proyecto" o selecciona un proyecto existente
3. Completa la configuración del proyecto
4. Toma nota del **Project ID** (ej: `mi-proyecto-equipos`)

### 2. Habilitar Firestore Database

1. En el menú lateral, ve a **Build > Firestore Database**
2. Haz clic en "Crear base de datos"
3. Selecciona modo de inicio (recomendado: **Modo de prueba** para desarrollo)
4. Selecciona una ubicación (ej: `us-central1`)

### 3. Configurar Authentication

1. En el menú lateral, ve a **Build > Authentication**
2. Haz clic en "Comenzar"
3. En la pestaña "Sign-in method", habilita **Email/Password**
4. Crea un usuario:
   - Ve a la pestaña "Users"
   - Haz clic en "Agregar usuario"
   - Ingresa email: `admin@tuempresa.com`
   - Ingresa contraseña: `tu-password-seguro`
   - Guarda el usuario

### 4. Obtener Web API Key

1. En el menú lateral, haz clic en el ícono de configuración ⚙️
2. Selecciona "Configuración del proyecto"
3. Baja hasta la sección "Tus apps"
4. Si no tienes una app web, haz clic en el ícono `</>` (Web)
5. Registra la app (puedes llamarla "EQUIPOS-PyQT6")
6. En "SDK setup and configuration", copia el **Web API Key** (empieza con `AIza...`)

### 5. Configurar Reglas de Seguridad (Importante)

Para desarrollo, puedes usar estas reglas en Firestore:

```javascript
rules_version = '2';
service cloud.firestore {
  match /databases/{database}/documents {
    // Permitir lectura/escritura solo a usuarios autenticados
    match /{document=**} {
      allow read, write: if request.auth != null;
    }
  }
}
```

Para producción, debes crear reglas más específicas según tus necesidades de seguridad.

## Configuración en la Aplicación

### Primera Vez

1. **Inicia la aplicación**
   ```bash
   python main_qt.py
   ```

2. **Si Firestore no está configurado**, la app te pedirá configurarlo:
   - Haz clic en "Sí" cuando se te pregunte
   - Se abrirá el diálogo "Configuración de Fuente de Datos"

3. **Completa los campos**:
   - **Fuente de datos**: Selecciona "Firestore"
   - **Project ID**: El ID de tu proyecto Firebase (ej: `mi-proyecto-equipos`)
   - **API Key**: Tu Web API Key de Firebase (ej: `AIzaSyA...`)
   - **Email**: El email del usuario que creaste (ej: `admin@tuempresa.com`)
   - **Contraseña**: La contraseña del usuario

4. **Prueba la conexión**:
   - Haz clic en "Probar Conexión"
   - Deberías ver un mensaje de "Conexión exitosa"

5. **Guarda la configuración**:
   - Haz clic en "Guardar"
   - Reinicia la aplicación

### Migración desde SQLite

Si tienes datos en una base de datos SQLite existente:

1. **Abre el menú "Herramientas"**
2. **Selecciona "Migrar desde SQLite a Firestore..."**
3. **Selecciona tu archivo .db** con los datos existentes
4. **Haz clic en "Iniciar Migración"**
5. **Espera** a que se complete (puede tomar varios minutos)

La migración:
- ✅ Copia TODOS los datos de SQLite a Firestore
- ✅ No elimina ni modifica la base SQLite original
- ✅ Evita duplicados si se ejecuta múltiples veces (por ID)

## Backups

### Configurar Carpeta de Backups

1. Ve a **Configuración > Configurar Carpeta de Backups...**
2. Selecciona una carpeta en tu sistema (ej: `D:\Backups\Equipos`)
3. La configuración se guarda automáticamente

### Crear un Backup

1. Ve a **Herramientas > Crear Backup SQLite desde Firestore...**
2. Verifica la carpeta de destino
3. Haz clic en "Crear Backup"
4. El backup se creará con un nombre único: `backup_firestore_YYYYMMDD_HHMMSS.db`

Los backups son útiles para:
- 📦 Tener copias de seguridad locales
- 📊 Análisis offline de datos
- 🔄 Migrar a otro sistema
- 💾 Archivo histórico

## Verificar Conexión

Para verificar que Firestore está funcionando:

1. Ve a **Herramientas > Verificar Conexión Firestore**
2. Deberías ver un mensaje de "Conexión exitosa"

Si hay errores:
- ✅ Verifica tu conexión a internet
- ✅ Revisa las credenciales en **Configuración > Configurar Fuente de Datos**
- ✅ Verifica que las reglas de Firestore permitan acceso autenticado
- ✅ Revisa que el usuario existe en Firebase Authentication

## Cambiar entre Fuentes de Datos

### De Firestore a SQLite

Si necesitas volver temporalmente a SQLite:

1. Ve a **Configuración > Configurar Fuente de Datos...**
2. Cambia "Fuente de datos" a "SQLite"
3. Guarda y reinicia la aplicación

### De SQLite a Firestore

1. Ve a **Configuración > Configurar Fuente de Datos...**
2. Cambia "Fuente de datos" a "Firestore"
3. Completa/verifica las credenciales de Firestore
4. Guarda y reinicia la aplicación

## Solución de Problemas

### Error: "No se pudo conectar a Firestore"

**Posibles causas:**
- Sin conexión a internet
- Credenciales incorrectas
- Project ID incorrecto
- API Key inválida

**Solución:**
1. Verifica tu conexión a internet
2. Ve a Firebase Console y confirma:
   - Project ID correcto
   - API Key correcto (Project Settings)
   - Usuario existe en Authentication
3. Vuelve a configurar en la app

### Error: "Permission denied" en Firestore

**Causa:** Las reglas de seguridad de Firestore no permiten el acceso.

**Solución:**
1. Ve a Firebase Console > Firestore Database > Rules
2. Verifica que las reglas permitan acceso a usuarios autenticados
3. Ejemplo de reglas básicas (arriba en este documento)

### La migración falla parcialmente

**Causa:** Algunos datos pueden tener formatos incompatibles.

**Solución:**
- La migración continúa incluso si algunos registros fallan
- Revisa el log de migración para ver qué falló
- Los errores se registran pero no detienen el proceso
- Puedes ejecutar la migración nuevamente (evita duplicados)

### Datos no aparecen después de migración

**Verificación:**
1. Ve a Firebase Console > Firestore Database
2. Revisa las colecciones creadas:
   - `proyectos`
   - `equipos`
   - `clientes`
   - `operadores`
   - `alquileres`
   - `transacciones`
   - `pagos`
   - `mantenimientos`

## Estructura de Datos en Firestore

Las colecciones en Firestore replican la estructura de SQLite:

```
/proyectos/{proyecto_id}
  - id: number
  - nombre: string
  - descripcion: string
  - moneda: string
  - cuenta_principal: string

/equipos/{equipo_id}
  - id: number
  - proyecto_id: number
  - nombre: string
  - marca: string
  - modelo: string
  - categoria: string
  - activo: boolean

/clientes/{cliente_id}
  - id: number
  - nombre: string
  - [otros campos específicos]

/operadores/{operador_id}
  - id: number
  - nombre: string
  - [otros campos específicos]

/alquileres/{alquiler_id}
  - id: string (UUID)
  - proyecto_id: number
  - equipo_id: number
  - cliente_id: number
  - fecha: timestamp
  - [otros campos]

/transacciones/{transaccion_id}
  - id: string (UUID)
  - proyecto_id: number
  - tipo: string ("Ingreso" | "Gasto")
  - monto: number
  - fecha: timestamp
  - [otros campos]

/pagos/{pago_id}
  - id: number
  - proyecto_id: number
  - operador_id: number
  - monto: number
  - fecha: timestamp
  - [otros campos]

/mantenimientos/{mantenimiento_id}
  - id: number
  - equipo_id: number
  - fecha: timestamp
  - [otros campos]
```

## Archivos de Configuración

### `app_settings.json`

Este archivo guarda la configuración de la aplicación:

```json
{
  "data_source": "firestore",
  "firestore": {
    "project_id": "mi-proyecto-equipos",
    "email": "admin@tuempresa.com",
    "password": "********",
    "api_key": "AIzaSy************"
  },
  "backup": {
    "sqlite_folder": "./backups"
  }
}
```

⚠️ **IMPORTANTE**: Este archivo contiene credenciales sensibles.
- ✅ Está incluido en `.gitignore` (no se sube a Git)
- ✅ Mantén backups seguros de este archivo
- ✅ No lo compartas públicamente

## Ventajas de Firestore

✅ **Acceso desde múltiples dispositivos**: Varios usuarios pueden trabajar simultáneamente  
✅ **Sincronización en tiempo real**: Los cambios se reflejan instantáneamente  
✅ **Backups automáticos**: Firebase hace backups automáticos  
✅ **Escalabilidad**: Crece con tu negocio sin problemas  
✅ **Disponibilidad**: 99.95% de uptime garantizado  
✅ **Seguridad**: Autenticación y reglas de acceso integradas  

## Soporte

Si tienes problemas o dudas:
1. Revisa esta documentación
2. Revisa los logs en `progain.log`
3. Contacta al administrador del sistema
