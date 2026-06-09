# 20 — Aplicación Android Nativa (Fase 7)

## Tecnologías Utilizadas
- **Kotlin**: Lenguaje de programación principal.
- **Jetpack Compose**: Framework declarativo para la construcción de la interfaz de usuario (UI).
- **Retrofit & OkHttp**: Clientes para el consumo de la API REST del backend.
- **DataStore**: Almacenamiento local seguro para tokens de autenticación JWT.
- **Firebase Cloud Messaging (FCM)**: Recepción de notificaciones push de eventos de la agenda.

## Configuración y Entorno

### Base URL del Backend
El endpoint al cual se conecta la app se define de manera centralizada en `NetworkConfig.kt`.
- **Emulador Local**: Utiliza `http://10.0.2.2:5000` para apuntar al localhost de la máquina de desarrollo.
- **Dispositivo Físico Local**: Debe configurarse con la IP local de la computadora (ej. `http://192.168.1.XX:5000`) y asegurarse de que tanto el dispositivo como la computadora estén en la misma red Wi-Fi.
- **Backend Local**: Ejecutar `python run.py --host=0.0.0.0` para que acepte conexiones externas de la red.
- **Producción**: Reemplazar con el dominio oficial del servidor (ej. `https://api.agenda.ecuamatriz.com`).

### Configuración de Firebase (`google-services.json`)
Para que la app pueda recibir notificaciones y utilizar los servicios de Firebase:
1. Crear un proyecto en la consola de Firebase.
2. Agregar una aplicación Android con el Application ID `com.agenda.movil` (debe coincidir con `namespace` en `build.gradle.kts`).
3. Descargar el archivo `google-services.json` proporcionado por la consola.
4. Ubicar el archivo en la ruta exacta `android/app/google-services.json`.

> [!NOTE]
> Por motivos de seguridad, `google-services.json` está excluido del control de versiones mediante `.gitignore`. Si el repositorio es clonado en un nuevo entorno, será necesario volver a colocar este archivo para poder compilar. Se ha provisto un archivo dummy que permite compilar pero que debe ser reemplazado para conectarse al backend real.

## Arquitectura y Funcionalidad
La app sigue una arquitectura moderna dividida por paquetes lógicos:
- `ui`: Contiene las pantallas (`LoginScreen`, `HomeScreen`, `MeetingDetailScreen`, `QrScannerScreen`) y la configuración de navegación (`Navigation.kt`).
- `data/api`: Modelos de petición/respuesta (DTOs), `NetworkConfig.kt` y configuración de Retrofit.
- `data/local`: Gestión del almacenamiento de tokens mediante Jetpack DataStore.
- `theme`: Configuración de la paleta de colores corporativos Ecuamatriz (Primary `#003091`, Secondary `#0057FF`, Accent `#48C9E3`).

### Endpoints Consumidos
- `POST /api/auth/login`: Autenticación y obtención de tokens JWT.
- `POST /api/auth/devices/register`: Registro del token FCM.
- `GET /api/mobile/meetings/today`: Reuniones del día actual.
- `GET /api/mobile/meetings/upcoming`: Próximas reuniones confirmadas.
- `GET /api/mobile/meetings/invitations`: Invitaciones pendientes.
- `POST /api/mobile/meetings/<id>/accept`: Aceptar invitación.
- `POST /api/mobile/meetings/<id>/reject`: Rechazar invitación.
- `GET /api/mobile/meetings/<id>`: Detalle de reunión.
- `GET /api/mobile/attendance/meeting/<id>/my-status`: Estado de asistencia.
- `POST /api/mobile/attendance/qr/<token>`: Marcación de asistencia con token QR.

## Pruebas y Compilación

### Levantar el Backend
1. Levantar Docker Desktop y los servicios de infraestructura:
   ```bash
   docker compose up -d
   docker compose ps
   ```
2. Inicializar entorno y BD (en la carpeta `backend`):
   ```bash
   $env:FLASK_APP="run.py"
   flask db upgrade
   python scripts/seed_all.py
   python run.py --host=0.0.0.0
   ```

### Compilar y Ejecutar Android
1. Desde la carpeta `android`, limpiar y compilar en modo Debug:
   ```bash
   ./gradlew clean
   ./gradlew assembleDebug
   ```
   *Nota en Windows PowerShell: `.\gradlew.bat clean` y `.\gradlew.bat assembleDebug`*.
2. El APK se generará y puede instalarse en el emulador o teléfono.

## Estado Actual (Cierre Fase 8 - Endurecimiento)
- **FCM**: La app obtiene correctamente el token de FirebaseMessaging y lo registra en el backend. Sin embargo, el envío de notificaciones push está deshabilitado en el backend (`FCM_ENABLED=false` en el seeder), por lo que por el momento se registra pero no se envía push real.
- **Autenticación y Sesión**: Implementada la renovación automática de tokens JWT (`refresh_token`) usando `OkHttp Authenticator`. Si el token expira y la renovación falla, la aplicación cierra la sesión automáticamente, limpia las preferencias y redirige a la pantalla de Login con un mensaje claro al usuario.
- **QR / Asistencia**: Se ha implementado de forma nativa el escaneo de códigos QR usando `CameraX` y `ML Kit Barcode Scanning`. El usuario puede escanear el QR directamente o introducir la URL/token de forma manual a través de una opción secundaria de (Debug/Manual). El código maneja el ciclo completo y muestra alertas en caso de fallo, éxito o sesiones expiradas.

## Limitaciones y Pendientes
- **Pruebas de Cámara**: Las funcionalidades de `CameraX` para el escáner QR deben probarse de preferencia en un dispositivo Android físico, ya que algunos emuladores no cuentan con la interfaz o recursos adecuados para inyectar imágenes en la cámara simulada con fiabilidad.
- Funcionalidades como: **Reportes, Actas, Fichas técnicas, Audio, Transcripción, PDF, Excel y Panel administrativo móvil** no forman parte del alcance de la app base actual y quedan pospuestas.
